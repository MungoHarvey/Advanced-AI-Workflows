<#
.SYNOPSIS
    Runs Herdr with HOME pinned to the real Windows profile.

.DESCRIPTION
    On a domain-joined Windows machine with an AD "Home directory" attribute, the logon
    process sets HOMEDRIVE and HOMEPATH to the mapped network home (here, M:\). Tools that
    resolve their configuration through HOME, HOMEDRIVE/HOMEPATH, or a POSIX-style ~ then
    look in the wrong place.

    Herdr honours HOME when HOME is set, and falls back to USERPROFILE when it is not. That
    makes the failure shell-specific rather than machine-wide:

      - Windows PowerShell leaves HOME unset, so herdr falls back to USERPROFILE and has
        always resolved correctly.
      - Git Bash exports HOME=/m/, so herdr probes M:\.claude\, M:\.codex\,
        M:\.config\opencode\, and M:\.cursor\ - none of which exist - and reports every
        integration as "not installed". The integrations are installed and current on C:.

    This launcher pins HOME, HOMEDRIVE, and HOMEPATH from USERPROFILE for the child process
    only, then runs herdr with whatever arguments it was given. It changes nothing outside
    the process it starts. Use tools/herdr-env.sh for the Git Bash side.

    USERPROFILE is the correct source. It is set by the session for the actual local profile
    and is not affected by the AD home-folder attribute. Never resolve a global path through
    HOME, ~, or HOMEDRIVE on this machine.

.PARAMETER Assert
    Do not run herdr. Instead check that every runtime in the AAW target set resolves under
    USERPROFILE and reports something other than "not installed". Exits 0 on success, 1 on
    failure. This is the doctor assertion: it fails loudly rather than resolving to the wrong
    drive silently.

    Only the target set is checked. Herdr ships integrations for many runtimes this project
    does not use, and "not installed" is the correct answer for those.

.EXAMPLE
    ./tools/herdr-env.ps1 integration status

.EXAMPLE
    ./tools/herdr-env.ps1 -Assert
    # Fails if the environment has drifted back to the network home.

.NOTES
    Background: .advanced-plans/evidence/2026-08-26-baseline-audit.md section 7.
    A user-level registry override of HOME/HOMEDRIVE/HOMEPATH is also in place, but the AD
    home-folder attribute is reasserted at each logon, so that override cannot be relied on
    alone. This launcher is the guard that makes the outcome deterministic either way.
#>
[CmdletBinding()]
param(
    [switch]$Assert,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$HerdrArgs
)

$ErrorActionPreference = 'Stop'

if (-not $env:USERPROFILE) {
    Write-Error 'USERPROFILE is not set. Cannot resolve the real profile; refusing to guess.'
    exit 2
}

$profileRoot = (Resolve-Path -LiteralPath $env:USERPROFILE).Path

# Pin for this process and everything it starts. Nothing outside is touched.
$env:HOME      = $profileRoot
$env:HOMEDRIVE = $profileRoot.Substring(0, 2)
$env:HOMEPATH  = $profileRoot.Substring(2)

if ($Assert) {
    # The AAW v0.2 target runtime set. Herdr supports many more; those are not our concern.
    $targets = @('claude', 'codex', 'opencode', 'cursor')

    Write-Output "profile root : $profileRoot"
    Write-Output "target set   : $($targets -join ', ')"
    Write-Output ''

    $status = & herdr integration status 2>&1
    $failures = @()

    foreach ($name in $targets) {
        $line = $status | Where-Object { $_ -match "^\s*$name\s*:" } | Select-Object -First 1

        if (-not $line) {
            $failures += "$name : herdr reported no status line at all"
            continue
        }

        Write-Output "  $line"

        if ($line -match 'not installed') {
            $failures += "$name : reports ""not installed"""
        }
        if ($line -match '\(([A-Za-z]:[^)]*)\)') {
            $reported = $Matches[1]
            if (-not $reported.StartsWith($profileRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
                $failures += "$name : path resolves outside the profile - $reported"
            }
        }
    }
    Write-Output ''

    if ($failures.Count -gt 0) {
        Write-Output 'ASSERTION FAILED'
        $failures | Sort-Object -Unique | ForEach-Object { Write-Output "  - $_" }
        Write-Output ''
        Write-Output 'The environment has drifted. Run Herdr through this launcher, and see'
        Write-Output 'baseline audit section 7 for why HOME cannot be trusted on this machine.'
        exit 1
    }

    Write-Output 'ASSERTION PASSED - every target runtime resolves under the real profile.'
    exit 0
}

if (-not $HerdrArgs -or $HerdrArgs.Count -eq 0) {
    Write-Output 'Usage: ./tools/herdr-env.ps1 <herdr arguments>'
    Write-Output '       ./tools/herdr-env.ps1 -Assert'
    exit 2
}

& herdr @HerdrArgs
exit $LASTEXITCODE
