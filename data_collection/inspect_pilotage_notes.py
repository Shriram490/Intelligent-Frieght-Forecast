from pathlib import Path

file_path = Path("../data/processed/paradip_sor_2026_27.txt")

print("Searching Pilotage & Towage notes...")

text = file_path.read_text(encoding="utf-8")

start = text.find("3.4 Pilotage")
end = text.find("3.5", start)

section = text[start:end]

print("\n" + "=" * 80)
print("PILOTAGE & TOWAGE SECTION")
print("=" * 80)

print(section)