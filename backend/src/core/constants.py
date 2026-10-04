# One name per value the ML returns. Every record gets a row for each of
# these, found or not, in this order.
EXPECTED_FIELDS = [
    # describe the whole document - the same on every plot's record
    "owner_name",
    "guardian_name",
    "owner_address",
    "khata_number",
    "total_holding_area",
    "village",
    "tehsil",
    "district",
    "tenure_type",
    "total_plots",
    "mutation_status",
    "registration_statement",
    "copy_number",
    "certification_date",
    "signed_by",
    "fees_received",
    # describe one plot - different on every record
    "khasra_number",
    "plot_area",
    "occupier_share",
    "share_area",
    "land_classification",
    "previous_khata_numbers",
]

CRITICAL_FIELDS = [
    "owner_name",
    "khasra_number",
    "plot_area",
]

# On the ML's scale, which is 0-100 today. If it switches to 0-1, make this 0.8.
CONFIDENCE_THRESHOLD = 80

# LGD check: how alike (0-100) a place name must be to an official one to count
# as the same place. Try pairs with try.py at the repo root.
LGD_MATCH_CUTOFF = 70

# The ML names the template it read a file with, e.g. "WB_BN_ROR_V1"; the first
# part is the state. Maps it to the LGD state code. Add a state when the ML gets
# a template for it - an unknown state is checked against all of India.
EXTRACTOR_STATES = {
    "WB": 19,   # West Bengal
}
