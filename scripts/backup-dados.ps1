# Backup COMPLETO (estrutura + dados) do banco do controle veterinario. Rode antes de mexer
# em migration ou de qualquer carga em lote.
#
# A senha vem do .env (nunca fica gravada aqui): assim o script pode ir para o
# git sem carregar a credencial do banco junto.
$linhaUrl = Get-Content "$PSScriptRoot\..\.env" | Where-Object { $_ -match '^DATABASE_URL=' }
if ($linhaUrl -match 'postgresql\+psycopg2://([^:]+):([^@]*)@([^:/]+):(\d+)/(.+)$') {
    $usuario = $Matches[1]; $senha = $Matches[2]; $servidor = $Matches[3]; $porta = $Matches[4]; $banco = $Matches[5]
} else {
    Write-Error "Nao consegui ler DATABASE_URL do .env"
    exit 1
}

$data = Get-Date -Format "yyyy-MM-dd_HHmm"
$destino = "C:\Projetos\controleveterinario\schema_bd\backup_completo_$data.sql"
$env:PGPASSWORD = $senha
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -n public -O -x `
  -h $servidor -p $porta -U $usuario -d $banco -f $destino
Remove-Item Env:PGPASSWORD
Write-Host "Backup gerado em $destino"
