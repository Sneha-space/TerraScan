// How the review screen names and groups the fields the backend sends.
// A field name not listed here still shows, under "Other", with a label
// made from its name - so a new field from the ML never disappears.

export const FIELD_LABELS = {
  khasra_number: "Khasra number",
  plot_area: "Plot area",
  occupier_share: "Owner's share",
  share_area: "Share area",
  land_classification: "Land class",
  previous_khata_numbers: "Previous khata numbers",
  owner_name: "Owner",
  guardian_name: "Guardian",
  owner_address: "Address",
  tenure_type: "Tenure",
  village: "Village (mouza)",
  tehsil: "Block or tehsil",
  district: "District",
  khata_number: "Khata number",
  total_holding_area: "Total holding area",
  total_plots: "Plots in khatian",
  mutation_status: "Mutation record",
  copy_number: "Copy number",
  certification_date: "Certified on",
  signed_by: "Signed by",
  fees_received: "Fees",
  registration_statement: "Certification statement",
};

export const FIELD_GROUPS = [
  {
    title: "This plot",
    fields: [
      "khasra_number",
      "plot_area",
      "occupier_share",
      "share_area",
      "land_classification",
      "previous_khata_numbers",
    ],
  },
  { title: "Owner", fields: ["owner_name", "guardian_name", "owner_address", "tenure_type"] },
  { title: "Location", fields: ["village", "tehsil", "district"] },
  {
    title: "Khatian",
    fields: ["khata_number", "total_holding_area", "total_plots", "mutation_status"],
  },
  {
    title: "Certified copy",
    fields: [
      "copy_number",
      "certification_date",
      "signed_by",
      "fees_received",
      "registration_statement",
    ],
  },
];

export function fieldLabel(name) {
  if (FIELD_LABELS[name]) return FIELD_LABELS[name];
  const words = name.replace(/_/g, " ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** Fields arranged into FIELD_GROUPS, unknown names collected under "Other". */
export function groupFields(fields) {
  const byName = new Map(fields.map((f) => [f.name, f]));
  const placed = new Set();
  const groups = FIELD_GROUPS.map((group) => ({
    title: group.title,
    fields: group.fields
      .filter((name) => byName.has(name))
      .map((name) => {
        placed.add(name);
        return byName.get(name);
      }),
  })).filter((group) => group.fields.length > 0);

  const other = fields.filter((f) => !placed.has(f.name));
  if (other.length) groups.push({ title: "Other", fields: other });
  return groups;
}

const STATUS_LABELS = {
  needs_review: "Needs review",
  auto_approved: "Auto-approved",
  verified: "Verified",
};

export const statusLabel = (status) => STATUS_LABELS[status] ?? status;

const DOCUMENT_STATUS_LABELS = {
  processing: "Waiting to be read",
  done: "Read",
  failed: "Couldn't be read",
};

export const documentStatusLabel = (status) => DOCUMENT_STATUS_LABELS[status] ?? status;

// mutation_status holds a flag the ML sets, not text from the page
const MUTATION_LABELS = { found: "Found", not_found: "Not found", info_required: "Needs checking" };

/** The English value as it should read on screen. */
export function englishValue(field) {
  const value = field.display_value;
  if (field.name === "mutation_status" && value) return MUTATION_LABELS[value] ?? value;
  return value;
}
