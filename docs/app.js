const { useState, useEffect } = React;

const API_BASE = "http://127.0.0.1:8000";

function TopBar({ route, setRoute }) {
  const items = [
    { id: "home", label: "Home" },
    { id: "compare", label: "Compare" },
    { id: "ingest", label: "Ingest Circular" },
    { id: "receipt", label: "Receipt Upload" },
    { id: "contribute", label: "Contribute" },
    { id: "sources", label: "Sources" }
  ];

  return (
    <div className="topbar">
      <div className="brand">CUFPI Food Price Tool</div>
      <div className="nav">
        {items.map(item => (
          <button
            key={item.id}
            className={route === item.id ? "active" : ""}
            onClick={() => setRoute(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function Home({ setRoute }) {
  return (
    <div>
      <div className="card" style={{ marginTop: 16 }}>
        <h3>New: Ingest Circulars</h3>
        <div className="small">
          Use the <strong>Ingest Circular</strong> tab to upload a PDF/image or paste a link.
        </div>
        <button className="primary" style={{ marginTop: 8 }} onClick={() => setRoute("ingest")}>
          Ingest a Circular
        </button>
      </div>
      <div className="hero">
        <div className="card">
          <h3>Find a product</h3>
          <div className="searchbar">
            <input placeholder="e.g., whole milk, 1 gallon" />
            <button className="primary" onClick={() => setRoute("compare")}>Search</button>
          </div>
          <div className="small" style={{ marginTop: 8 }}>Recent: eggs, brown rice, apples</div>
        </div>
        <div className="card">
          <h3>Best price today</h3>
          <div className="small">Top 5 cheapest items across stores.</div>
          <ul>
            <li>Bananas — $0.49/lb</li>
            <li>Chicken thighs — $1.99/lb</li>
            <li>Oats — $2.79/18oz</li>
            <li>Yogurt — $0.79/ea</li>
            <li>Milk — $3.49/gal</li>
          </ul>
        </div>
      </div>

      <div className="tilegrid">
        <div className="tile" onClick={() => setRoute("compare")}>Compare Circulars</div>
        <div className="tile" onClick={() => setRoute("compare")}>Compare Instacart</div>
        <div className="tile" onClick={() => setRoute("receipt")}>Upload Receipt</div>
      </div>
    </div>
  );
}

function Compare() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState([]);
  const [selected, setSelected] = useState(null);
  const [prices, setPrices] = useState([]);

  const runSearch = async () => {
    if (!query) return;
    const res = await fetch(`${API_BASE}/products?query=${encodeURIComponent(query)}`);
    const data = await res.json();
    setProducts(data);
    setSelected(null);
    setPrices([]);
  };

  const loadPrices = async (productId) => {
    const res = await fetch(`${API_BASE}/products/${productId}/prices`);
    const data = await res.json();
    setPrices(data.prices || []);
  };

  return (
    <div className="section">
      <div className="card">
        <h3>Compare Prices</h3>
        <div className="filters">
          <input
            placeholder="Search product"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="primary" onClick={runSearch}>Search</button>
        </div>

        {products.length > 0 && (
          <div className="card" style={{ marginBottom: 12 }}>
            <div className="small">Select a product to compare prices:</div>
            {products.map(p => (
              <div key={p.id} style={{ marginTop: 6 }}>
                <button className="primary" onClick={() => { setSelected(p); loadPrices(p.id); }}>
                  {p.name}
                </button>
              </div>
            ))}
          </div>
        )}

        <table className="table">
          <thead>
            <tr>
              <th>Store</th>
              <th>Price</th>
              <th>Date</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {prices.map((p, idx) => (
              <tr key={idx}>
                <td>{p.store_id}</td>
                <td>${p.price}</td>
                <td>{p.date}</td>
                <td>{p.source}</td>
              </tr>
            ))}
            {prices.length === 0 && (
              <tr><td colSpan="4" className="small">No prices yet. Try ingesting circular data.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ReceiptUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const upload = async () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_BASE}/receipts/upload`, { method: "POST", body: form });
    const data = await res.json();
    setStatus(`Uploaded receipt #${data.receipt_id}`);
  };

  return (
    <div className="section">
      <div className="card">
        <h3>Upload Receipt</h3>
        <div className="dropzone">
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        </div>
        <button className="primary" style={{ marginTop: 12 }} onClick={upload}>Upload</button>
        <div className="small" style={{ marginTop: 8 }}>{status}</div>
      </div>
    </div>
  );
}

function IngestCircular() {
  const [stores, setStores] = useState([]);
  const [storeId, setStoreId] = useState("");
  const [tab, setTab] = useState("upload");
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [items, setItems] = useState([]);
  const [ocrText, setOcrText] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/stores`).then(r => r.json()).then(setStores);
  }, []);

  const runOcr = async () => {
    if (!file || !storeId) return;
    setStatus("Processing...");
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${API_BASE}/ocr/run`, { method: "POST", body: form });
    const data = await res.json();
    setItems(data.items || []);
    setOcrText(data.text || "");
    setStatus(`Found ${data.items?.length || 0} items`);
  };

  const saveFromText = async () => {
    if (!ocrText || !storeId) return;
    const payload = {
      store_id: Number(storeId),
      source_url: file ? `upload:${file.name}` : "upload",
      text: ocrText
    };
    const res = await fetch(`${API_BASE}/ingestion/circulars/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    setStatus(`Saved ${data.count || 0} items`);
  };

  const fetchFromUrl = async () => {
    if (!url || !storeId) return;
    setStatus("Fetching...");
    const payload = { store_id: Number(storeId), source_url: url };
    const res = await fetch(`${API_BASE}/ingestion/circulars/from-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    setItems(data.items || []);
    setStatus(`Saved ${data.count || 0} items`);
  };

  return (
    <div className="section">
      <div className="card">
        <h3>Ingest Circular</h3>
        <div className="filters">
          <select value={storeId} onChange={(e) => setStoreId(e.target.value)}>
            <option value="">Select store</option>
            {stores.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>

        <div className="tabs">
          <button className={tab === "upload" ? "active" : ""} onClick={() => setTab("upload")}>Upload File</button>
          <button className={tab === "link" ? "active" : ""} onClick={() => setTab("link")}>Use Link</button>
        </div>

        {tab === "upload" && (
          <div>
            <div className="dropzone">
              <input type="file" onChange={(e) => setFile(e.target.files[0])} />
            </div>
            <button className="primary" style={{ marginTop: 12 }} onClick={runOcr}>Process Circular</button>
            <button className="primary" style={{ marginTop: 12, marginLeft: 8 }} onClick={saveFromText}>Save to Database</button>
          </div>
        )}

        {tab === "link" && (
          <div className="filters">
            <input placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
            <button className="primary" onClick={fetchFromUrl}>Fetch & Process</button>
          </div>
        )}

        <div className="small" style={{ marginTop: 8 }}>{status}</div>

        {items.length > 0 && (
          <div className="card" style={{ marginTop: 12 }}>
            <h3>Detected Items</h3>
            <ul>
              {items.map((it, idx) => (
                <li key={idx}>{it.name || it.raw_text} — ${it.price}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

function Contribute() {
  const [stores, setStores] = useState([]);
  const [storeId, setStoreId] = useState("");
  const [product, setProduct] = useState("");
  const [price, setPrice] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/stores`).then(r => r.json()).then(setStores);
  }, []);

  const submit = async () => {
    const body = { store_id: Number(storeId), product_name: product, price: Number(price) };
    const res = await fetch(`${API_BASE}/crowd/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    const data = await res.json();
    setStatus(`Submitted ${data.submission_id}`);
  };

  return (
    <div className="section">
      <div className="card">
        <h3>Submit a Price</h3>
        <div className="filters">
          <select value={storeId} onChange={(e) => setStoreId(e.target.value)}>
            <option value="">Select store</option>
            {stores.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <input placeholder="Product (e.g., eggs 12ct)" value={product} onChange={(e) => setProduct(e.target.value)} />
          <input placeholder="Price" value={price} onChange={(e) => setPrice(e.target.value)} />
          <button className="primary" onClick={submit}>Submit</button>
        </div>
        <div className="small">{status}</div>
      </div>
    </div>
  );
}

function Sources() {
  const [sources, setSources] = useState([]);
  const [status, setStatus] = useState("");

  const load = () => {
    fetch(`${API_BASE}/sources`).then(r => r.json()).then(data => setSources(data.sources || []));
  };

  useEffect(() => { load(); }, []);

  const save = async () => {
    const payload = { sources };
    await fetch(`${API_BASE}/sources`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    setStatus("Saved");
  };

  return (
    <div className="section">
      <div className="card">
        <h3>Sources</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Store</th>
              <th>URL</th>
              <th>Enabled</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((s, idx) => (
              <tr key={idx}>
                <td><input value={s.store} onChange={(e) => {
                  const next = [...sources]; next[idx].store = e.target.value; setSources(next);
                }} /></td>
                <td><input value={s.url} onChange={(e) => {
                  const next = [...sources]; next[idx].url = e.target.value; setSources(next);
                }} /></td>
                <td>
                  <input type="checkbox" checked={s.enabled} onChange={(e) => {
                    const next = [...sources]; next[idx].enabled = e.target.checked; setSources(next);
                  }} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button className="primary" onClick={save}>Save</button>
        <div className="small">{status}</div>
      </div>
    </div>
  );
}

function App() {
  const [route, setRoute] = useState("home");

  let page = <Home setRoute={setRoute} />;
  if (route === "compare") page = <Compare />;
  if (route === "ingest") page = <IngestCircular />;
  if (route === "receipt") page = <ReceiptUpload />;
  if (route === "contribute") page = <Contribute />;
  if (route === "sources") page = <Sources />;

  return (
    <div className="app">
      <TopBar route={route} setRoute={setRoute} />
      {page}
      <div className="footer-note">
        Demo UI. API expected at {API_BASE}.
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
