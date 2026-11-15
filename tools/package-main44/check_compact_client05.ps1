$ErrorActionPreference = 'Stop'
$taskRoot480 = [IO.Path]::GetDirectoryName($PSCommandPath)
$fixturePath480 = Join-Path $taskRoot480 '../package-main28/client05-readonly.exe'
$zipPath480 = Join-Path $taskRoot480 'build-0.480.0-compact/ForeverThai-0.480.0-main44-COMBINED.zip'
$asm480 = [Reflection.Assembly]::LoadFrom($fixturePath480)
$updates480 = $asm480.GetType('ForeverThaiLauncher.Updates', $true)
$manifest480 = @{
    schema = 1
    version = '0.480.0'
    bytes = 31488257
    sha256 = '7bdbf55bf8f38974a8a55cc80cc0e83dbed1df951b69bf21f1d8f3291ca48208'
    url = 'https://raw.githubusercontent.com/cryptokao/foreverthai-updates/de5f12db434efc70ab0c3945fb44209fe639f139/output/ForeverThai-0.480.0-main28-COMBINED.zip'
} | ConvertTo-Json
$package480 = $updates480.GetMethod('ParseManifest').Invoke($null, @([string]$manifest480))
if (-not $updates480.GetMethod('IsNewer').Invoke($null, @('0.480.0','0.470.0'))) { throw 'Not newer' }
$fileField480 = $package480.GetType().GetField('FilePath')
if ($null -eq $fileField480) { throw 'Unexpected release schema' }
$fileField480.SetValue($package480, $zipPath480)
$verified480 = $package480.GetType().GetMethod('OpenVerified').Invoke($package480, @())
try {
    $stage480 = Join-Path $taskRoot480 'client05-isolated-compact-stage'
    if (Test-Path -LiteralPath $stage480) {
        if (@(Get-ChildItem -LiteralPath $stage480 -Force).Count -ne 0) { throw 'Refuse to overwrite a nonempty test stage' }
    }
    [IO.Directory]::CreateDirectory($stage480) | Out-Null
    $report480 = [Action[string]] { param($message480) }
    $asm480.GetType('ForeverThaiLauncher.Installer', $true).GetMethod('Extract').Invoke(
        $null, @($verified480, [string]$stage480, [Threading.CancellationToken]::None, $report480, '0.480.0')) | Out-Null
} finally { $verified480.Dispose() }
$files480 = @(Get-ChildItem -LiteralPath (Join-Path $stage480 'ForeverThai') -File -Recurse)
if ($files480.Count -ne 183) { throw 'Missing extracted files' }
$out480 = @{
    status = 'PASSED_ACTUAL_CUSTOMER05_PARSER_HASH_AND_ISOLATED_EXTRACT'
    tested_assembly_version = $asm480.GetName().Version.ToString()
    manifest_parse = $true
    newer_than_live_0470 = $true
    package_length_sha256_verified = $true
    actual_installer_extract_183_files = $true
    target = $stage480
    game_install_or_UI_launch = $false
    real_game_acceptance = $false
}
$out480 | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot480 'build-0.480.0-compact/client05-compatibility.json') -Encoding UTF8
$out480 | ConvertTo-Json
