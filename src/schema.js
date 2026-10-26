export const initialForm = {
  gender: 'Female', senior_citizen: '0', partner: 'Yes', dependents: 'No', tenure: '',
  contract: 'Month-to-month', phone_service: 'Yes', multiple_lines: 'No', internet_service: 'Fiber optic',
  online_security: 'No', online_backup: 'No', device_protection: 'No', tech_support: 'No',
  streaming_tv: 'No', streaming_movies: 'No', monthly_charges: '', total_charges: '',
  payment_method: 'Electronic check', paperless_billing: 'Yes',
};

export const internetFields = ['online_security', 'online_backup', 'device_protection', 'tech_support', 'streaming_tv', 'streaming_movies'];
const yesNo = ['Yes', 'No'];
const internetOptions = ['Yes', 'No', 'No internet service'];

export const fieldGroups = [
  { title: 'Customer', fields: [
    ['gender', 'Gender', ['Female', 'Male']], ['senior_citizen', 'Senior citizen', ['0', '1']],
    ['partner', 'Partner', yesNo], ['dependents', 'Dependents', yesNo],
  ] },
  { title: 'Account', fields: [
    ['tenure', 'Tenure (months)'], ['contract', 'Contract', ['Month-to-month', 'One year', 'Two year']],
  ] },
  { title: 'Services', fields: [
    ['phone_service', 'Phone service', yesNo], ['multiple_lines', 'Multiple lines', ['Yes', 'No', 'No phone service']],
    ['internet_service', 'Internet service', ['DSL', 'Fiber optic', 'No']],
    ['online_security', 'Online security', internetOptions], ['online_backup', 'Online backup', internetOptions],
    ['device_protection', 'Device protection', internetOptions], ['tech_support', 'Tech support', internetOptions],
    ['streaming_tv', 'Streaming TV', internetOptions], ['streaming_movies', 'Streaming movies', internetOptions],
  ] },
  { title: 'Billing', fields: [
    ['monthly_charges', 'Monthly charges ($)'], ['total_charges', 'Total charges ($)'],
    ['payment_method', 'Payment method', ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)']],
    ['paperless_billing', 'Paperless billing', yesNo],
  ] },
];

export function updateForm(current, name, value) {
  const next = { ...current, [name]: value };
  if (name === 'phone_service') next.multiple_lines = value === 'No' ? 'No phone service' : 'No';
  if (name === 'internet_service') {
    for (const field of internetFields) next[field] = value === 'No' ? 'No internet service' : current[field] === 'No internet service' ? 'No' : current[field];
  }
  return next;
}

export function toPayload(form) {
  return { ...form, senior_citizen: Number(form.senior_citizen), tenure: Number(form.tenure), monthly_charges: Number(form.monthly_charges), total_charges: Number(form.total_charges) };
}
