from pathlib import Path

input_file = Path("../data/processed/paradip_sor_2026_27.txt")
output_file = Path("../data/processed/wharfage_section.txt")

print("Reading Paradip tariff text...")

text = input_file.read_text(encoding="utf-8")

start_marker = "2.1 Wharfage charges:"
end_marker = "2.2 Wharfage on Containers"

start = text.find(start_marker)
end = text.find(end_marker)

if start == -1:
    print("ERROR: Start of Section 2.1 not found.")
    raise SystemExit

if end == -1:
    print("ERROR: End of Section 2.1 not found.")
    raise SystemExit

wharfage_section = text[start:end]

output_file.write_text(
    wharfage_section,
    encoding="utf-8"
)

print("\nWharfage section extracted successfully!")
print("Characters:", len(wharfage_section))
print("Output:", output_file)

print("\n===== WHARFAGE SECTION =====\n")
print(wharfage_section)