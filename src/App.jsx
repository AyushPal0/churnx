import { useEffect, useMemo, useRef, useState } from 'react';
import { apiRequest, normalizePrediction } from './api';
import { fieldGroups, initialForm, internetFields, toPayload, updateForm } from './schema';
import './App.css';

const navItems = [
  { id: 'overview', label: 'Overview', icon: '◌' },
  { id: 'customers', label: 'Customers', icon: '◉' },
  { id: 'predictions', label: 'Predictions', icon: '✦' },
  { id: 'insights', label: 'Insights', icon: '◒' },
  { id: 'model', label: 'Model', icon: '◇' },
];

export default function App() {
  const [activePage, setActivePage] = useState('overview');
  const [workspace, setWorkspace] = useState({ status: 'loading', dashboard: null, model: null, history: [], error: '' });
  const [reload, setReload] = useState(0);
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const submitting = useRef(false);
  const resultRef = useRef(null);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(90000)]);
    Promise.all([apiRequest('/health', { signal }), apiRequest('/dashboard', { signal }), apiRequest('/model-info', { signal }), apiRequest('/predictions', { signal })])
      .then(([health, dashboard, model, history]) => {
        if (active && health.model_loaded) setWorkspace({ status: 'ready', dashboard, model, history: history.predictions, error: '' });
      })
      .catch((err) => {
        if (active) setWorkspace({ status: 'error', dashboard: null, model: null, history: [], error: err.name === 'TimeoutError' ? 'The service took too long to respond. Please retry.' : err.message });
      });
    return () => { active = false; controller.abort(); };
  }, [reload]);

  const ready = workspace.status === 'ready';
  const customers = workspace.dashboard?.customers || [];
  const highRiskCount = customers.filter((customer) => customer.risk === 'High').length;
  const averageRisk = customers.length ? customers.reduce((sum, customer) => sum + customer.churnProbability, 0) / customers.length : 0;
  const activeLabel = navItems.find((item) => item.id === activePage).label;

  async function handlePredict(event) {
    event.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setPending(true); setError(''); setResult(null);
    try {
      const payload = await apiRequest('/predict', { method: 'POST', body: JSON.stringify(toPayload(form)) });
      const prediction = normalizePrediction(payload);
      setResult(prediction);
      setWorkspace((current) => ({ ...current, history: [{ id: payload.prediction_id, probability: payload.churn_probability, risk: payload.risk_level, prediction: payload.prediction, model_version: payload.model_version, created_at: new Date().toISOString() }, ...current.history].slice(0, 50) }));
      requestAnimationFrame(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }));
    } catch (err) {
      setError(err.name === 'TimeoutError' ? 'Analysis timed out. Please try again.' : err.message);
    } finally { submitting.current = false; setPending(false); }
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand-block"><div className="brand-mark">C</div><div><strong>ChurnX</strong><span>Customer intelligence</span></div></div>
      <div className="sidebar-label">WORKSPACE</div>
      <nav aria-label="Main navigation">{navItems.map((item) => <button key={item.id} aria-label={item.label} aria-current={activePage === item.id ? 'page' : undefined} className={`nav-item ${activePage === item.id ? 'active' : ''}`} onClick={() => setActivePage(item.id)}><span className="nav-icon" aria-hidden="true">{item.icon}</span><span>{item.label}</span></button>)}</nav>
      <div className="sidebar-footer"><div className="model-status"><span className={`status-dot ${ready ? '' : 'offline'}`} /><div><strong>{ready ? 'Model online' : workspace.status === 'loading' ? 'Connecting…' : 'Service offline'}</strong><span>{workspace.model?.model_name || 'Awaiting service'}</span></div></div><span className="sidebar-version">{workspace.model?.version || 'ChurnX'} · IBM Telco</span></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><div><span className="breadcrumb">Workspace / {activeLabel}</span><h1>{activeLabel}</h1></div><div className="topbar-actions"><span className={`mode-pill ${ready ? 'connected' : ''}`}><span />{ready ? 'Live inference' : workspace.status === 'loading' ? 'Connecting' : 'Offline'}</span><span className="date-label">{new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata' }).format(new Date())}</span><div className="avatar">CX</div></div></header>
      {workspace.status === 'loading' && <div className="service-notice" role="status">Connecting to the prediction service… After inactivity, this can take about a minute.</div>}
      {workspace.status === 'error' && <div className="error-message service-notice" role="alert"><span>{workspace.error || 'The service is unavailable.'}</span><button className="secondary-button" onClick={() => { setWorkspace((current) => ({ ...current, status: 'loading' })); setReload((current) => current + 1); }}>Retry connection</button></div>}
      {activePage === 'overview' && <Overview dashboard={workspace.dashboard} model={workspace.model} averageRisk={averageRisk} highRiskCount={highRiskCount} navigate={setActivePage} />}
      {activePage === 'customers' && <CustomersPage customers={customers} ready={ready} />}
      {activePage === 'predictions' && <section className="prediction-layout">
        <PageIntro eyebrow="INDIVIDUAL SCORING" title="Analyze a customer" text="Estimate churn risk from the account, services, and billing information in a customer snapshot." />
        <div className="prediction-columns">
          <form className="panel prediction-form" onSubmit={handlePredict} aria-busy={pending}>
            <div className="form-header"><div><span className="panel-kicker">CUSTOMER PROFILE</span><h3>Customer information</h3></div><span className="required-note">All fields required</span></div>
            <fieldset className="form-fields" disabled={pending}>{fieldGroups.map((group) => <FormGroup key={group.title} group={group} form={form} onChange={(event) => { setForm((current) => updateForm(current, event.target.name, event.target.value)); setError(''); setResult(null); }} />)}</fieldset>
            {error && <div className="error-message" role="alert">{error}</div>}
            <button className="primary-button full-button" type="submit" disabled={pending || !ready}>{pending ? 'Analyzing customer…' : 'Analyze churn risk'}<span aria-hidden="true">→</span></button>
            <p className="form-footnote">Charges are in USD, matching the source dataset. Risk bands: low below 30%, medium 30–60%, high 60% and above.</p>
          </form>
          <div ref={resultRef} aria-live="polite"><PredictionResult result={result} pending={pending} /></div>
        </div>
        <History history={workspace.history} />
      </section>}
      {activePage === 'insights' && <InsightsPage dashboard={workspace.dashboard} />}
      {activePage === 'model' && <ModelPage model={workspace.model} />}
      <footer><span>ChurnX Intelligence Platform</span><span>Snapshot risk scoring · {workspace.model?.version || 'Waiting for model'}</span></footer>
    </main>
  </div>;
}

function PageIntro({ eyebrow, title, text }) {
  return <div className="page-intro compact"><span className="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{text}</p></div>;
}

function Overview({ dashboard, model, averageRisk, highRiskCount, navigate }) {
  const customers = dashboard?.customers || [];
  return <>
    <section className="hero-section"><div><span className="eyebrow">CUSTOMER RETENTION INTELLIGENCE</span><h2>Know who is leaving<br /><em>before they do.</em></h2><p>Understand customer churn risk, explore the signals behind each score, and prioritize your next retention conversation.</p><button className="primary-button hero-button" onClick={() => navigate('predictions')}>Analyze a customer <span>→</span></button></div><div className="hero-aside"><span className="eyebrow">HELD-OUT TEST ROC-AUC</span><strong>{model ? model.metrics.roc_auc.toFixed(3) : '—'}</strong><p>{model?.model_name || 'Model results unavailable'}<br />{model ? `${model.split.test.toLocaleString()} unseen test records` : 'Connect the prediction service'}</p><button className="text-button aside-link" onClick={() => navigate('model')}>View model details →</button></div></section>
    <section className="metric-grid"><Metric label="Customers scored" value={dashboard ? dashboard.records.toLocaleString() : '—'} note="IBM Telco sample dataset" accent="lime" /><Metric label="High-risk customers" value={dashboard ? highRiskCount.toLocaleString() : '—'} note="Model probability ≥60%" accent="rose" /><Metric label="Average churn risk" value={dashboard ? `${averageRisk.toFixed(1)}%` : '—'} note="Across scored dataset" accent="amber" /><Metric label="Historical churn rate" value={dashboard ? `${dashboard.churn_rate.toFixed(1)}%` : '—'} note="Observed dataset labels" accent="blue" /></section>
    <section className="overview-grid"><div className="panel overview-card"><div className="section-heading"><div><span className="panel-kicker">RETENTION WORKFLOW</span><h3>From a customer profile to a retention decision.</h3></div><span className="spark-icon">✦</span></div><div className="workflow">{[['01', 'Score', 'Estimate probability from account and service data.'], ['02', 'Explain', 'Explore how profile attributes affect the model score.'], ['03', 'Prioritize', 'Focus attention on accounts with elevated risk.']].map(([number, title, text]) => <div className="workflow-step" key={number}><span>{number}</span><div><h4>{title}</h4><p>{text}</p></div></div>)}</div></div><div className="panel quick-card"><span className="panel-kicker">QUICK START</span><h3>Start with a customer profile</h3><p>Score one customer using the same fields that the trained model sees.</p><button className="secondary-button" onClick={() => navigate('predictions')}>Open prediction form <span>↗</span></button><div className="schema-note"><span className="status-dot" />19 validated profile fields</div></div></section>
    <section className="panel recent-card"><div className="section-heading"><div><span className="panel-kicker">CUSTOMER MONITORING</span><h3>Highest-risk accounts</h3></div><button className="text-button" onClick={() => navigate('customers')}>View all →</button></div><CustomerTable customers={[...customers].sort((a, b) => b.churnProbability - a.churnProbability).slice(0, 5)} /></section>
    {dashboard && <p className="data-context">{dashboard.scoring_context}</p>}
  </>;
}

function FormGroup({ group, form, onChange }) {
  return <div className="form-group"><div className="group-heading"><h4>{group.title}</h4></div><div className="fields-grid">{group.fields.map(([name, label, options]) => {
    const unavailable = (internetFields.includes(name) && form.internet_service === 'No') || (name === 'multiple_lines' && form.phone_service === 'No');
    const allowed = options?.filter((option) => name === 'multiple_lines' ? form.phone_service === 'No' ? option === 'No phone service' : option !== 'No phone service' : internetFields.includes(name) ? form.internet_service === 'No' ? option === 'No internet service' : option !== 'No internet service' : true);
    return <label className="field" key={name}><span>{label}</span>{options ? <select name={name} value={form[name]} onChange={onChange} disabled={unavailable} required>{allowed.map((option) => <option key={option} value={option}>{name === 'senior_citizen' ? option === '1' ? 'Yes' : 'No' : option}</option>)}</select> : <input name={name} type="number" min="0" max={name === 'tenure' ? 1200 : name === 'monthly_charges' ? 1000000 : 1000000000} step={name === 'tenure' ? 1 : .01} value={form[name]} onChange={onChange} required />}</label>;
  })}</div></div>;
}

function PredictionResult({ result, pending }) {
  if (!result) return <div className="panel result-card empty-state"><div className="empty-mark">✦</div><span className="panel-kicker">LATEST ASSESSMENT</span><h3>{pending ? 'Analyzing customer…' : 'No prediction yet'}</h3><p>{pending ? 'Evaluating the profile with the trained model.' : 'Complete the customer profile to see a churn probability, risk level, and explanation.'}</p><div className="result-flow"><span>Profile</span><b>→</b><span>Model</span><b>→</b><span>Risk</span></div></div>;
  return <div className="panel result-card"><div className="result-top"><span className="panel-kicker">LATEST ASSESSMENT</span><span className="result-source">{result.modelVersion}</span></div><div className={`score-ring ${result.risk.toLowerCase()}`} style={{ '--score': `${result.probability * 3.6}deg` }}><div><strong>{result.probability}%</strong><span>churn probability</span></div></div><span className={`risk-badge ${result.risk.toLowerCase()}`}>{result.risk} risk</span><h3>{result.classification}</h3><p className="result-summary">Risk bands and the model’s classification threshold serve different purposes. This estimate does not predict a cancellation date.</p><div className="reasons"><span className="panel-kicker">FACTORS RAISING THIS SCORE</span>{result.reasons.length ? result.reasons.map((reason, index) => <div key={reason}><b>{index + 1}</b><span>{reason}</span></div>) : <p>No individual field raised the score materially versus the training reference.</p>}<p className="form-footnote">{result.explanationMethod}</p></div></div>;
}

function CustomersPage({ customers, ready }) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('All');
  const [sort, setSort] = useState('risk');
  const [page, setPage] = useState(0);
  const visible = useMemo(() => customers.filter((customer) => `${customer.id} ${customer.contract} ${customer.internetService}`.toLowerCase().includes(query.toLowerCase())).filter((customer) => filter === 'All' || customer.risk === filter).sort((a, b) => sort === 'risk' ? b.churnProbability - a.churnProbability : b.tenure - a.tenure), [customers, query, filter, sort]);
  const pages = Math.max(1, Math.ceil(visible.length / 25));
  const current = Math.min(page, pages - 1);
  return <section className="page-section"><PageIntro eyebrow="SCORED CUSTOMER DATASET" title="Customers" text="Find accounts with elevated risk and explore the profiles behind each score." /><div className="panel table-card"><div className="table-toolbar"><label className="search-box"><input aria-label="Search customers" value={query} onChange={(event) => { setQuery(event.target.value); setPage(0); }} placeholder="Search ID, contract, internet service…" /></label><div className="toolbar-controls"><div className="filter-tabs">{['All', 'High', 'Medium', 'Low'].map((item) => <button key={item} aria-pressed={filter === item} className={filter === item ? 'selected' : ''} onClick={() => { setFilter(item); setPage(0); }}>{item}</button>)}</div><select className="sort-select" aria-label="Sort customers" value={sort} onChange={(event) => { setSort(event.target.value); setPage(0); }}><option value="risk">Highest risk</option><option value="tenure">Longest tenure</option></select></div></div><CustomerTable customers={visible.slice(current * 25, (current + 1) * 25)} /><div className="pagination"><span>{ready ? `${visible.length.toLocaleString()} matching customers` : 'Customer data unavailable'}</span><div><button className="secondary-button" disabled={current === 0} onClick={() => setPage(current - 1)}>Previous</button><span>{current + 1} / {pages}</span><button className="secondary-button" disabled={current >= pages - 1} onClick={() => setPage(current + 1)}>Next</button></div></div></div></section>;
}

function CustomerTable({ customers }) {
  return <div className="table-wrap"><table><thead><tr>{['Customer ID', 'Tenure', 'Contract', 'Monthly charges', 'Churn probability', 'Risk'].map((label) => <th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{customers.map((customer) => <tr key={customer.id}><td><div className="customer-cell"><span className="customer-avatar" aria-hidden="true">{customer.id.slice(-2)}</span><div><strong>{customer.id}</strong><span>{customer.internetService} · {customer.techSupport === 'Yes' ? 'Tech support' : customer.internetService === 'No' ? 'No internet' : 'No tech support'}</span></div></div></td><td>{customer.tenure} mo</td><td>{customer.contract}</td><td>${customer.monthlyCharges.toFixed(2)}</td><td><div className="probability-cell"><span className="mini-bar"><i className={customer.risk.toLowerCase()} style={{ width: `${customer.churnProbability}%` }} /></span><b>{customer.churnProbability}%</b></div></td><td><span className={`risk-badge ${customer.risk.toLowerCase()}`}>{customer.risk}</span></td></tr>)}</tbody></table>{!customers.length && <div className="no-results">No customer records to display.</div>}</div>;
}

function InsightsPage({ dashboard }) {
  const charts = [['Contract', 'contract'], ['tenure', 'tenure'], ['InternetService', 'internet service'], ['PaymentMethod', 'payment method'], ['TechSupport', 'technical support'], ['OnlineSecurity', 'online security']];
  const features = (dashboard?.feature_importance || []).slice(0, 8);
  const maxImportance = Math.max(...features.map((item) => item.value), .001);
  return <section className="page-section"><PageIntro eyebrow="PATTERN EXPLORATION" title="Insights" text="Explore observed churn rates in the historical dataset and the features that matter to model ranking." /><div className="insight-grid">{charts.map(([key, label]) => <ChartCard key={key} title={`Churn rate by ${label}`} data={dashboard?.groups[key] || []} />)}</div><div className="panel feature-card"><span className="panel-kicker">GLOBAL EXPLAINABILITY</span><h3>Validation permutation importance</h3><p className="data-context">Drop in ROC-AUC when a feature is shuffled across validation customers. Larger values indicate greater model reliance.</p><div className="feature-list">{features.map((feature, index) => <div className="feature-row" key={feature.label}><span className="feature-rank">{index + 1}</span><span className="feature-label">{feature.label}</span><span className="feature-track"><i style={{ width: `${feature.value / maxImportance * 100}%` }} /></span><b>{feature.value.toFixed(3)}</b></div>)}{!features.length && <p className="no-results">Model analysis unavailable.</p>}</div></div><div className="insight-note"><span className="status-dot" /><div><strong>Association, not causation</strong><p>Historical patterns and model sensitivity support prioritization; retention actions need separate evaluation.</p></div></div></section>;
}

function ChartCard({ title, data }) {
  return <div className="panel chart-card"><span className="panel-kicker">OBSERVED CHURN RATE</span><h3>{title}</h3><div className="bar-chart">{data.map((item) => <div className="bar-row" key={item.label}><div className="bar-label"><span>{item.label} <small>({item.count.toLocaleString()})</small></span><b>{item.value}%</b></div><div className="bar-track"><i style={{ width: `${item.value}%` }} /></div></div>)}{!data.length && <p className="no-results">Dataset analysis unavailable.</p>}</div></div>;
}

function ModelPage({ model }) {
  return <section className="page-section"><PageIntro eyebrow="MODEL OPERATIONS" title="Model" text="Inspect the selected classifier, measured test results, and comparison with alternative models." />{!model ? <div className="panel no-results">Connect the service to load trained model metadata.</div> : <>
    <div className="model-grid"><div className="panel model-summary"><div className="model-orb">ML</div><span className="panel-kicker">SELECTED BY CROSS-VALIDATION</span><h3>{model.model_name}</h3><p>A serialized preprocessing and classification pipeline evaluated against an untouched test partition.</p><div className="model-details">{[['Version', model.version], ['Dataset', model.dataset], ['Trained (UTC)', model.training_date.slice(0, 10)], ['Train / validation / test', `${model.split.train} / ${model.split.validation} / ${model.split.test}`], ['Classification threshold', model.threshold], ['Risk boundaries', '30% / 60%']].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div></div><div className="panel metrics-card"><span className="panel-kicker">HELD-OUT TEST RESULTS</span><h3>Performance overview</h3><div className="model-metrics">{[['ROC-AUC', 'roc_auc'], ['PR-AUC', 'pr_auc'], ['Recall', 'recall'], ['Precision', 'precision'], ['F1 score', 'f1'], ['Brier score', 'brier_score']].map(([label, key]) => <div key={key}><span>{label}</span><strong>{model.metrics[key].toFixed(3)}</strong></div>)}</div><div className="metric-disclaimer">{model.split.cv_folds}-fold stratified cross-validation selects the model. Validation data selects the classification threshold; the test partition is used only for final evaluation.</div></div></div>
    <div className="panel recent-card"><span className="panel-kicker">CROSS-VALIDATION COMPARISON</span><div className="table-wrap"><table><thead><tr>{['Candidate', 'ROC-AUC', 'PR-AUC', 'Recall', 'F1'].map((label) => <th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{model.comparison.map((row) => <tr key={row.model}><td>{row.model}{row.model === model.model_name ? ' · selected' : ''}</td>{['roc_auc', 'pr_auc', 'recall', 'f1'].map((key) => <td key={key}>{row[key].toFixed(3)}</td>)}</tr>)}</tbody></table></div></div>
    <div className="panel model-contract"><div><span className="panel-kicker">REPRODUCIBLE INFERENCE</span><h3>One pipeline from training to prediction</h3></div><div className="contract-points"><span>Validated profile</span><b>→</b><span>Preprocessing</span><b>→</b><span>Probability</span><b>→</b><span>Risk</span></div></div>
  </>}</section>;
}

function History({ history }) {
  return <section className="panel history-card"><span className="panel-kicker">PREDICTION HISTORY</span><h3>Recent individual assessments</h3><div className="table-wrap"><table><thead><tr>{['Time', 'Probability', 'Risk', 'Classification', 'Model version'].map((label) => <th scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{history.map((item) => <tr key={item.id}><td>{new Date(item.created_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}</td><td>{(item.probability * 100).toFixed(2)}%</td><td><span className={`risk-badge ${item.risk.toLowerCase()}`}>{item.risk}</span></td><td>{item.prediction ? 'Likely to churn' : 'Likely to stay'}</td><td>{item.model_version}</td></tr>)}</tbody></table>{!history.length && <p className="no-results">Your completed assessments will appear here.</p>}</div></section>;
}

function Metric({ label, value, note, accent }) {
  return <div className="metric-card"><div className="metric-label"><span>{label}</span><i className={accent} /></div><strong>{value}</strong><p>{note}</p></div>;
}
