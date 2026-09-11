import hashlib
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

repo_root = Path(".").resolve()

# 1. Update audit_git_status.txt
res_status = subprocess.run(["git", "status"], capture_output=True, text=True, encoding="utf-8")
with open("audit_git_status.txt", "w", encoding="utf-8") as f:
    f.write(res_status.stdout + "\n" + res_status.stderr)

# 2. Update audit_changes.patch
res_diff = subprocess.run(["git", "diff"], capture_output=True, text=True, encoding="utf-8")
res_cached = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, encoding="utf-8")
with open("audit_changes.patch", "w", encoding="utf-8") as f:
    f.write(res_diff.stdout)
    if res_cached.stdout:
        f.write("\n# --- CACHED CHANGES ---\n" + res_cached.stdout)

files_to_package = [
    # Phase 2 Core Services & Scripts
    ("services/taxonomy_state_machine.py", "Maquina de estados, DurableCheckpoint atomico, hash SHA-256 canonico e runner em lotes de 10"),
    ("services/content_taxonomy_classifier.py", "Classificador base de taxonomia com verificacao e normalizacao"),
    ("scripts/build_pilot_dataset.py", "Seletor deterministico com teto de 10 por especialidade e deteccao de bloqueio"),
    ("scripts/run_pilot_calibration.py", "Orquestrador de execucao, metricas e geracao da planilha de revisao CSV"),
    ("scripts/package_audit_zip.py", "Script de empacotamento, inventario e verificacao de integridade"),
    
    # Models & Database Migration
    ("models.py", "Modelos SQLAlchemy com ContentTaxonomyClassification, MedicalTaxonomyNode e Version"),
    ("alembic/versions/20260910_20_unified_content_taxonomy.py", "Migracao de banco para tabelas sombra da taxonomia v1"),
    ("pyproject.toml", "Configuracao do ambiente de teste com pythonpath"),
    
    # Controlled Taxonomy Registry & Manifests
    ("data/taxonomy_registry_pilot_v0_1.json", "Registro canonico controlado v0.1 de especialidades, temas, assuntos e competencias"),
    ("data/pilot_manifest_3000.json", "Manifesto da Fase 1"),
    ("data/pilot_selection_report.json", "Relatorio formal da selecao amostral e diagnostico de bloqueio"),
    
    # Pilot Outputs, Checkpoint & Logs
    ("data/pilot_inputs_100.jsonl", "Arquivo de entradas canonicas (bloqueado por falta de dados diversificados na fonte)"),
    ("data/pilot_classifications_100.jsonl", "Resultados finais das classificacoes (bloqueado por falta de dados diversificados na fonte)"),
    ("data/pilot_checkpoint.json", "Checkpoint duravel atomico com registro do status bloqueado"),
    ("data/pilot_execution_log.jsonl", "Log sequencial de eventos de execucao e deteccao de bloqueio"),
    ("data/pilot_metrics.json", "Metricas consolidadas do piloto"),
    ("data/pilot_review_sheet.csv", "Planilha CSV formatada para auditoria humana"),
    
    # Documentation & Runbook
    ("docs/PILOT_CLASSIFICATION_RUNBOOK.md", "Runbook operacional detalhado com passos de retomada e resolucao de bloqueio"),
    
    # Tests
    ("tests/test_taxonomy_pilot_validation.py", "Bateria completa de 12 testes automatizados das 15 garantias do protocolo"),
    
    # Audit Outputs
    ("audit_git_status.txt", "Saida completa de git status da auditoria"),
    ("audit_changes.patch", "Patch unificado de todas as alteracoes locais"),
    ("audit_test_results.txt", "Saida completa da execucao dos testes do pytest")
]

inventory_lines = [
    "=" * 80,
    "MEDSYNC - INVENTARIO DO PACOTE DE AUDITORIA (FASE 2 DE CALIBRACAO TAXONOMICA)",
    "=" * 80,
    "Data de geracao: 2026-09-11",
    f"Total de arquivos inventariados: {len(files_to_package) + 1}",
    "-" * 80,
    f"{'CAMINHO':<55} {'TAMANHO':>10}  {'SHA-256':<64}",
    "-" * 80,
]

for rel_p, desc in files_to_package:
    fp = repo_root / rel_p
    if not fp.exists():
        print(f"ERRO: Arquivo ausente: {rel_p}")
        continue
    sz = fp.stat().st_size
    with open(fp, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    inventory_lines.append(f"{rel_p:<55} {sz:>10}  {sha}")
    inventory_lines.append(f"  -> Descricao: {desc}")
    inventory_lines.append("")

inventory_p = repo_root / "audit_file_inventory.txt"
with open(inventory_p, "w", encoding="utf-8") as f:
    f.write("\n".join(inventory_lines) + "\n")

print(f"Inventario gerado em {inventory_p}")

zip_name = "medsync-taxonomia-piloto-fase2.zip"
zip_path = repo_root / zip_name

all_files = [rel_p for rel_p, _ in files_to_package] + ["audit_file_inventory.txt"]

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for rel_p in all_files:
        fp = repo_root / rel_p
        zipf.write(fp, arcname=rel_p)

with zipfile.ZipFile(zip_path, "r") as zipf:
    test_res = zipf.testzip()
    assert test_res is None, f"Corrupted file in zip: {test_res}"
    namelist = zipf.namelist()

print(f"ZIP criado com sucesso: {zip_path}")
print(f"Tamanho do ZIP: {zip_path.stat().st_size} bytes")
print(f"Total de arquivos no ZIP: {len(namelist)}")

forbidden = [".env", ".git", ".venv", "medsync.db", ".pyc", "__pycache__"]
for name in namelist:
    for f in forbidden:
        assert f not in name, f"Arquivo proibido encontrado no ZIP: {name}"

print("Zero arquivos proibidos ou credenciais no ZIP.")

art_dir = Path(r"C:\Users\rgust\.gemini\antigravity\brain\b18bc842-e738-4f4e-a3d4-dc9ed5d54829")
art_zip = art_dir / zip_name
shutil.copy(zip_path, art_zip)
print(f"Copiado para diretorio de artefatos: {art_zip} ({art_zip.stat().st_size} bytes)")
