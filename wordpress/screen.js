function exportFindings(result, data, sku, mapping, fictional, format) {
  const parts = [];
  let batch = [], bytes = 0;
  const encoder = new TextEncoder();
  const worksheets = {
    'Missing SKU': [sku], 'Repeated exact SKU': [sku], 'Missing selling unit': [mapping.uom],
    'Missing specification link': [mapping.spec], 'Malformed specification link': [mapping.spec],
    'Card and destination MPNs differ': [mapping.card, mapping.target],
    'Incomplete card comparison': [mapping.card, mapping.target]
  };

  function add(line) {
    const entry = line + '\r\n';
    bytes += encoder.encode(entry).length;
    if (bytes > 64 * 1024 * 1024) {
      throw new Error('This export exceeds 64 MiB. Split the source file to download all findings in smaller reports.');
    }
    batch.push(entry);
    if (batch.length === 256) {
      parts.push(batch.join(''));
      batch = [];
    }
  }

  function csvLine(fields) {
    return fields.map(value => {
      let text = String(value);
      if (/^[\s\u0000-\u001f]*[=+@\-＝＋＠－]|^[\t\r\n]/u.test(text)) text = "'" + text;
      return '"' + text.replaceAll('"', '""') + '"';
    }).join(',');
  }

  if (format === 'csv') {
    add(csvLine(['Source record', 'Selling SKU', 'Finding', 'Source column', 'Source value',
      'Comparison column', 'Comparison value', 'Suggested check', 'Reviewer', 'Decision', 'Approved value']));
  } else {
    add(fictional ? 'HWC Catalog Review | Fictional example' : 'HWC Catalog Review');
    add(summary(result));
    add('Checked: ' + result.checks.map(key => checkLabels[key]).join('; '));
    const skipped = Object.keys(checkLabels).filter(key => !result.checks.includes(key));
    add('Skipped: ' + (skipped.map(key => checkLabels[key]).join('; ') || 'none'));
    add('Record 1 is the first data row. Verify findings against the approved source.');
    if (!result.items.length) add('No findings under the checks listed above.');
  }
  for (const item of result.items) {
    if (format === 'text') {
      add('Record ' + item.record + ' | ' + item.reason + ' | ' + item.action);
      continue;
    }
    const row = data.rows[item.record - 1];
    const [first, second] = worksheets[item.reason] || [mapping.gtin];
    add(csvLine([item.record, row[sku], item.reason, data.headers[first], row[first],
      second === undefined ? '' : data.headers[second], second === undefined ? '' : row[second],
      item.action, '', '', '']));
  }
  if (batch.length) parts.push(batch.join(''));
  return parts;
}

function startCatalogReview() {
  const el = id => document.getElementById(id);
  const input = el('sample-file'), select = el('sample-sku'), status = el('sample-status');
  const optional = Object.fromEntries(Object.keys(fieldNames).filter(key => key !== 'sku')
    .map(key => [key, el('sample-' + key)]));
  let data = null, result = null, revision = 0, isExample = false;
  function reset() {
    revision++;
    isExample = false;
    data = null;
    result = null;
    status.textContent = '';
    select.replaceChildren();
    for (const field of Object.values(optional)) field.replaceChildren();
    el('optional-mapping').open = false;
    el('column-mapping').hidden = true;
    el('sample-results').hidden = true;
    el('findings').replaceChildren();
  }
  function render() {
    el('sample-results').hidden = true;
    result = null;
    if (!data || select.value === '') {
      status.textContent = 'Choose the column that contains your selling SKU.';
      return;
    }
    const mapping = Object.fromEntries(Object.entries(optional).map(([key, field]) => [key, Number(field.value)]));
    try {
      result = diagnose(data, Number(select.value), mapping);
    } catch (error) {
      status.textContent = error.message;
      return;
    }
    status.textContent = isExample ? 'Fictional example loaded.' : 'Report ready.';
    el('report-heading').textContent = isExample ? 'Fictional example report' : 'Your catalog report';
    el('finding-count').textContent = summary(result);
    el('checks-run').textContent = result.checks.map(key => checkLabels[key]).join(' · ');
    const skipped = Object.keys(checkLabels).filter(k => !result.checks.includes(k));
    el('skipped-checks').textContent = skipped.length ? 'Skipped for this file: ' + skipped.map(key => checkLabels[key]).join(' · ') + '.' : 'All five checks ran.';
    if ((mapping.card >= 0) !== (mapping.target >= 0)) {
      el('skipped-checks').textContent += ' Choose both part-number columns to run the card comparison.';
    }
    const previewLimit = 100;
    el('preview-note').textContent = result.items.length > previewLimit
      ? 'Showing the first 100 findings. Both downloads include every finding.'
      : '';
    const items = result.items.slice(0, previewLimit).map(x => {
      const li = document.createElement('li'), strong = document.createElement('strong');
      strong.textContent = 'Record ' + x.record + ' · ' + x.reason;
      li.append(strong, document.createTextNode(' — ' + x.action));
      return li;
    });
    el('findings').replaceChildren(...items);
    el('sample-results').hidden = false;
  }
  function loadText(text, fictional = false) {
    data = parseCatalog(text, Infinity);
    isExample = fictional;
    for (const [key, field] of Object.entries({sku: select, ...optional})) {
      const required = key === 'sku';
      const match = column(data.headers, key);
      field.replaceChildren();
      if (match === ambiguousColumn) {
        field.add(new Option('Multiple matches — choose a column', String(ambiguousColumn)));
        if (!required) el('optional-mapping').open = true;
      }
      if (!required || match !== ambiguousColumn) {
        field.add(new Option(required ? 'Select your SKU column' : 'Skip this field', required ? '' : '-1'));
      }
      data.headers.forEach((heading, i) => field.add(new Option(heading, String(i))));
      if (match >= 0) field.value = String(match);
    }
    el('column-mapping').hidden = false;
    render();
  }
  input.addEventListener('change', async () => {
    reset();
    const file = input.files[0], current = revision;
    if (!file) return;
    try {
      if (file.size > 4 * 1024 * 1024) throw new Error('Use a CSV of 4 MiB or less.');
      const bytes = await file.arrayBuffer();
      if (current !== revision) return;
      let text;
      try { text = new TextDecoder('utf-8', {fatal:true}).decode(bytes); }
      catch { throw new Error('Export a UTF-8 CSV and try again.'); }
      loadText(text);
    } catch (error) { if (current === revision) status.textContent = error.message; }
  });
  for (const field of [select, ...Object.values(optional)]) field.addEventListener('change', render);
  el('clear-sample').addEventListener('click', () => { reset(); input.value = ''; input.focus(); });
  el('try-example').addEventListener('click', () => {
    reset(); input.value = '';
    loadText('sku,uom,spec_url,card_mpn,destination_mpn\n001,EA,https://example.com/valve.pdf,V-10,V-10\n002,,spec.pdf,V-20,V-25\n002,PK,https://example.com/elbow.pdf,E-30,E-30', true);
  });
  function download(parts, type, filename) {
    const url = URL.createObjectURL(new Blob(parts, {type}));
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function downloadFindings(format, type, extension) {
    if (!result) return;
    const mapping = Object.fromEntries(Object.entries(optional).map(([key, field]) => [key, Number(field.value)]));
    try {
      const parts = exportFindings(result, data, Number(select.value), mapping, isExample, format);
      download(parts, type, (isExample ? 'fictional-' : '') + 'catalog-review.' + extension);
    } catch (error) {
      status.textContent = error.message;
    }
  }
  el('download-report').addEventListener('click', () => downloadFindings('text', 'text/plain;charset=utf-8', 'txt'));
  el('download-review').addEventListener('click', () => downloadFindings('csv', 'text/csv;charset=utf-8', 'csv'));
  window.addEventListener('pagehide', () => { reset(); input.value = ''; });
}
startCatalogReview();
