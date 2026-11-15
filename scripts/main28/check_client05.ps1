$ErrorActionPreference = 'Stop'
$taskRoot470 = [IO.Path]::GetDirectoryName($PSCommandPath)
$fixturePath470 = Join-Path $taskRoot470 'client05-readonly.exe'
$zipPath470 = Join-Path $taskRoot470 'build-0.470.0/ForeverThai-0.470.0-main28-COMBINED.zip'
$asm470 = [Reflection.Assembly]::LoadFrom($fixturePath470)
$updates470 = $asm470.GetType('ForeverThaiLauncher.Updates', $true)
$manifest470 = @{
    schema = 1
    version = '0.470.0'
    bytes = 29747971
    sha256 = 'a9c854976d2efac55b4821492714b7cf93dae627fbb77309d6bc820610cfb5e6'
    url = 'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/2da8d23f1863dcf92f7abd5666728f5f565e36b1/output/ForeverThai-0.470.0-main28-COMBINED.zip'
} | ConvertTo-Json
$package470 = $updates470.GetMethod('ParseManifest').Invoke($null, @([string]$manifest470))
if (-not $updates470.GetMethod('IsNewer').Invoke($null, @('0.470.0','0.463.1'))) { throw 'Not newer' }
$fileField470 = $package470.GetType().GetField('FilePath')
if ($null -eq $fileField470) { throw 'Unexpected release schema' }
$fileField470.SetValue($package470, $zipPath470)
$verified470 = $package470.GetType().GetMethod('OpenVerified').Invoke($package470, @())
try {
    $stage470 = Join-Path $taskRoot470 'client05-isolated-stage'
    if (Test-Path -LiteralPath $stage470) {
        if (@(Get-ChildItem -LiteralPath $stage470 -Force).Count -ne 0) { throw 'Refuse to overwrite a nonempty test stage' }
    }
    [IO.Directory]::CreateDirectory($stage470) | Out-Null
    $report470 = [Action[string]] { param($message470) }
    $asm470.GetType('ForeverThaiLauncher.Installer', $true).GetMethod('Extract').Invoke(
        $null, @($verified470, [string]$stage470, [Threading.CancellationToken]::None, $report470, '0.470.0')) | Out-Null
} finally { $verified470.Dispose() }
$files470 = @(Get-ChildItem -LiteralPath (Join-Path $stage470 'ForeverThai') -File -Recurse)
if ($files470.Count -ne 154) { throw 'Missing extracted files' }
$out470 = @{
    status = 'PASSED_ACTUAL_CUSTOMER05_PARSER_HASH_AND_ISOLATED_EXTRACT'
    tested_assembly_version = $asm470.GetName().Version.ToString()
    manifest_parse = $true
    newer_than_live_04631 = $true
    package_length_sha256_verified = $true
    actual_installer_extract_154_files = $true
    target = $stage470
    game_install_or_UI_launch = $false
    real_game_acceptance = $false
}
$out470 | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot470 'build-0.470.0/client05-compatibility.json') -Encoding UTF8
$out470 | ConvertTo-Json
