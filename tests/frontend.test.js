import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizePrediction } from '../src/api.js';
import { initialForm, internetFields, toPayload, updateForm } from '../src/schema.js';

test('payload uses 19 canonical API keys and numerical values', () => {
  const payload = toPayload({ ...initialForm, tenure: '12', monthly_charges: '89.5', total_charges: '1074' });
  assert.equal(Object.keys(payload).length, 19);
  assert.equal(payload.senior_citizen, 0);
  assert.equal(payload.monthly_charges, 89.5);
  assert.equal(payload.tenure, 12);
  assert.ok(!('monthlyCharges' in payload));
});

test('service dependencies remain valid when phone/internet availability changes', () => {
  const disconnected = updateForm(initialForm, 'internet_service', 'No');
  for (const field of internetFields) assert.equal(disconnected[field], 'No internet service');
  const restored = updateForm(disconnected, 'internet_service', 'DSL');
  for (const field of internetFields) assert.equal(restored[field], 'No');
  assert.equal(updateForm(initialForm, 'phone_service', 'No').multiple_lines, 'No phone service');
});

test('classification respects backend threshold decision separately from risk bands', () => {
  const result = normalizePrediction({ churn_probability: .38, prediction: 1, risk_level: 'MEDIUM', top_factors: ['Tenure'], model_version: 'test' });
  assert.equal(result.probability, 38);
  assert.equal(result.classification, 'Likely to churn');
  assert.equal(result.risk, 'Medium');
});

test('invalid responses never turn into a fabricated zero-risk score', () => {
  for (const probability of [undefined, null, '0.5', NaN, 3, -1]) {
    assert.throws(() => normalizePrediction({ churn_probability: probability, prediction: 0, risk_level: 'LOW' }));
  }
});
