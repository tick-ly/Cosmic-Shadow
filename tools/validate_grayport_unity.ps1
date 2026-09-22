param(
    [string]$Editor = $env:UNITY_EDITOR
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$project = Join-Path $root 'UnityProjectV2'
$reports = Join-Path $root 'docs\grayport'
if ([string]::IsNullOrWhiteSpace($Editor)) { throw 'Supply -Editor with the Unity 6000.4.0f1 executable path, or set UNITY_EDITOR.' }
if (-not (Test-Path -LiteralPath $Editor -PathType Leaf)) { throw "Editor missing: $Editor" }
$active = Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Where-Object {
    $_.CommandLine -and ($_.CommandLine.Replace('/','\').Contains($project))
}
if ($active) { throw "Project already opened by Unity PID $($active.ProcessId -join ',')." }
$steps = @()
function Run-Stage([string]$name, [string[]]$extra) {
    $log = Join-Path $reports ($name + '.log')
    $arguments = @('-batchmode', '-projectPath', ('"' + $project + '"'), '-logFile', ('"' + $log + '"')) + $extra
    $proc = Start-Process -FilePath $Editor -ArgumentList $arguments -WindowStyle Hidden -PassThru
    Write-Output "$name started, PID $($proc.Id)"
    $proc.WaitForExit()
    $script:steps += [ordered]@{stage=$name;exit_code=$proc.ExitCode;log=$log}
    $script:steps | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $reports 'unity-stages.json')
    if ($proc.ExitCode -ne 0) {
        Get-Content -LiteralPath $log -Tail 50
        throw "$name failed with exit code $($proc.ExitCode)"
    }
    if (Select-String -LiteralPath $log -Pattern 'error CS\d+|Scripts have compiler errors|No valid Unity Editor license' -Quiet) {
        throw "$name reported a compiler or license failure despite its exit code."
    }
}
Run-Stage 'unity-generate' @('-quit','-executeMethod','ShadowOfTheUniverse.V2.Editor.GrayportLevelBuilder.RebuildBatch')
Run-Stage 'unity-editmode' @('-runTests','-testPlatform','EditMode','-testResults',('"'+(Join-Path $reports 'editmode-results.xml')+'"'))
Run-Stage 'unity-playmode' @('-runTests','-testPlatform','PlayMode','-testFilter','ShadowOfTheUniverse.V2.Tests.GrayportPlayModeTests','-testResults',('"'+(Join-Path $reports 'playmode-results.xml')+'"'))
foreach ($name in @('editmode','playmode')) {
    [xml]$result = Get-Content -LiteralPath (Join-Path $reports ($name+'-results.xml')) -Raw
    $run = $result.'test-run'
    if (-not $run -or [int]$run.total -lt 1 -or [int]$run.failed -gt 0 -or $run.result -ne 'Passed') {
        throw "$name results did not prove a passing, nonempty test run."
    }
}
Run-Stage 'unity-render' @('-quit','-executeMethod','ShadowOfTheUniverse.V2.Editor.GrayportLevelBuilder.RenderPreviewBatch')
if (-not (Test-Path -LiteralPath (Join-Path $reports 'unity-preview.png'))) { throw 'Native render missing.' }
Write-Output 'UNITY_GRAYPORT_VALIDATION_PASSED'
