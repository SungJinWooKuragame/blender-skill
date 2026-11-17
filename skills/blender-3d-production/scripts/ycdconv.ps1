# Conversor YCD <-> CodeWalker XML usando CodeWalker.Core.dll (testado com CodeWalker 30 dev48).
# Rode com Windows PowerShell 5.1 (powershell.exe), que carrega o .NET Framework do CodeWalker.
# Uso:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ycdconv.ps1 xml2ycd <entrada.ycd.xml> <saida.ycd> [-CodeWalker <pasta>]
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ycdconv.ps1 ycd2xml <entrada.ycd> <saida.ycd.xml> [-CodeWalker <pasta>]
# Pasta do CodeWalker: parâmetro -CodeWalker ou variável de ambiente CODEWALKER_DIR.
param(
  [Parameter(Mandatory)][ValidateSet('xml2ycd','ycd2xml')][string]$Mode,
  [Parameter(Mandatory)][string]$In,
  [Parameter(Mandatory)][string]$Out,
  [string]$CodeWalker = $env:CODEWALKER_DIR
)
$ErrorActionPreference = 'Stop'
if (-not $CodeWalker) { throw "Informe -CodeWalker <pasta> ou defina CODEWALKER_DIR" }
[void][Reflection.Assembly]::LoadFrom((Join-Path $CodeWalker 'CodeWalker.Core.dll'))

if ($Mode -eq 'xml2ycd') {
  $doc = New-Object System.Xml.XmlDocument
  $doc.Load([string][IO.Path]::GetFullPath($In))
  $bytes = [CodeWalker.GameFiles.XmlMeta]::GetYcdData($doc)
  if (-not $bytes -or $bytes.Length -eq 0) { throw "Falha ao converter XML -> YCD" }
  [IO.File]::WriteAllBytes([IO.Path]::GetFullPath($Out), $bytes)
} else {
  $data = [IO.File]::ReadAllBytes([IO.Path]::GetFullPath($In))
  $ycd = New-Object CodeWalker.GameFiles.YcdFile
  $entry = [CodeWalker.GameFiles.RpfFile]::CreateResourceFileEntry([ref]$data, 0)
  $data = [CodeWalker.GameFiles.ResourceBuilder]::Decompress($data)
  $ycd.Load($data, $entry)
  [IO.File]::WriteAllText([IO.Path]::GetFullPath($Out), [CodeWalker.GameFiles.YcdXml]::GetXml($ycd))
}
"OK $Mode -> $Out ($((Get-Item -LiteralPath $Out).Length) bytes)"
