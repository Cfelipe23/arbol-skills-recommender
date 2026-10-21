(() => {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const NODE_WIDTH = 248;
  const NODE_HEIGHT = 126;
  const LEVEL_GAP = 300;
  const LEAF_GAP = 154;
  const X_MARGIN = 82;
  const Y_MARGIN = 126;
  const MIN_ZOOM = 0.18;
  const MAX_ZOOM = 1.65;

  const elements = {
    viewport: document.getElementById("map-viewport"),
    svg: document.getElementById("tree-svg"),
    loading: document.getElementById("map-loading"),
    search: document.getElementById("search-input"),
    searchCount: document.getElementById("search-count"),
    searchPrev: document.getElementById("search-prev"),
    searchNext: document.getElementById("search-next"),
    zoomOut: document.getElementById("zoom-out"),
    zoomIn: document.getElementById("zoom-in"),
    zoomValue: document.getElementById("zoom-value"),
    fitView: document.getElementById("fit-view"),
    themeToggle: document.getElementById("theme-toggle"),
    themeLabel: document.getElementById("theme-label"),
    themeColor: document.getElementById("theme-color"),
    headerCount: document.getElementById("header-count"),
    mapSummary: document.getElementById("map-summary"),
    footerStats: document.getElementById("footer-stats"),
    detailEmpty: document.getElementById("detail-empty"),
    detailContent: document.getElementById("detail-content"),
    detailType: document.getElementById("detail-type"),
    detailTitle: document.getElementById("detail-title"),
    detailBreadcrumb: document.getElementById("detail-breadcrumb"),
    detailInfo: document.getElementById("detail-info"),
    detailChildren: document.getElementById("detail-children"),
  };

  const state = { nodes: [], edges: [], root: null, width: 0, height: 0, zoom: 1, selected: null, matches: [], matchIndex: -1 };

  function setTheme(dark) {
    document.body.dataset.theme = dark ? "dark" : "light";
    elements.themeToggle.setAttribute("aria-pressed", String(dark));
    elements.themeToggle.setAttribute("aria-label", dark ? "Activar modo claro" : "Activar modo oscuro");
    elements.themeLabel.textContent = dark ? "Claro" : "Oscuro";
    elements.themeColor.setAttribute("content", dark ? "#151923" : "#f7f8fc");
    localStorage.setItem("decision-map-theme", dark ? "dark" : "light");
  }

  function svgElement(name, attributes = {}) {
    const element = document.createElementNS(SVG_NS, name);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value));
    return element;
  }

  function wrapText(value, limit) {
    const words = String(value || "").split(/\s+/);
    const lines = [];
    let line = "";
    for (const word of words) {
      const candidate = line ? `${line} ${word}` : word;
      if (candidate.length > limit && line) {
        lines.push(line);
        line = word;
      } else {
        line = candidate;
      }
    }
    if (line) lines.push(line);
    return lines.length ? lines : [""];
  }

  function layoutTree(source) {
    let leafIndex = 0;
    const nodes = [];
    const edges = [];

    function visit(data, parent = null, depth = 0) {
      const node = { data, parent, depth, children: [], x: 0, y: 0, element: null };
      nodes.push(node);
      for (const childData of data.hijos || []) {
        const child = visit(childData, node, depth + 1);
        node.children.push(child);
        edges.push({ from: node, to: child, element: null });
      }
      if (node.children.length) {
        node.y = node.children.reduce((total, child) => total + child.y, 0) / node.children.length;
      } else {
        node.y = Y_MARGIN + leafIndex * LEAF_GAP;
        leafIndex += 1;
      }
      node.x = X_MARGIN + depth * LEVEL_GAP;
      return node;
    }

    const root = visit(source);
    const deepest = Math.max(...nodes.map((node) => node.depth));
    return {
      root,
      nodes,
      edges,
      width: X_MARGIN * 2 + deepest * LEVEL_GAP + NODE_WIDTH,
      height: Y_MARGIN + Math.max(0, leafIndex - 1) * LEAF_GAP + NODE_HEIGHT / 2 + 80,
      leaves: leafIndex,
      depth: deepest + 1,
    };
  }

  function nodeKind(node) {
    if (!node.parent) return "start";
    if (!node.children.length) return "result";
    if (node.children.length > 1) return "question";
    return "branch";
  }

  function nodeTitle(node) {
    const kind = nodeKind(node);
    return kind === "start" ? "INICIO" : kind === "result" ? "RESULTADO" : kind === "question" ? "PREGUNTA" : "OPCIÓN";
  }

  function renderNode(node) {
    const kind = nodeKind(node);
    const group = svgElement("g", {
      class: `tree-node node-${kind}`,
      transform: `translate(${node.x}, ${node.y - NODE_HEIGHT / 2})`,
      tabindex: "0",
      role: "button",
      "aria-label": `${nodeTitle(node)}: ${node.data.valor}`,
      "data-node-id": state.nodes.indexOf(node),
    });
    const title = svgElement("title");
    title.textContent = node.data.valor;
    group.append(title);
    group.append(svgElement("rect", { class: "node-card", width: NODE_WIDTH, height: NODE_HEIGHT, rx: 14 }));
    group.append(svgElement("rect", { class: "node-accent", width: 4, height: 31, rx: 2 }));

    const heading = svgElement("text", { class: "node-heading", x: 17, y: 22 });
    heading.textContent = nodeTitle(node);
    group.append(heading);

    const lines = wrapText(node.data.valor, 30);
    const maxLines = node.children.length ? 4 : 3;
    const shownLines = lines.slice(0, maxLines);
    if (lines.length > maxLines) shownLines[maxLines - 1] = `${shownLines[maxLines - 1].slice(0, 25)}…`;

    const label = svgElement("text", { class: "node-label", x: NODE_WIDTH / 2, "text-anchor": "middle" });
    const labelStart = Math.max(47, (NODE_HEIGHT - (shownLines.length - 1) * 16) / 2 + 8);
    shownLines.forEach((line, index) => {
      const span = svgElement("tspan", { x: NODE_WIDTH / 2, y: labelStart + index * 16 });
      span.textContent = line;
      label.append(span);
    });
    group.append(label);

    if (kind === "result") {
      const parts = [node.data.tipo_salida, node.data.recomendacion].filter(Boolean);
      if (parts.length) {
        const detail = svgElement("text", { class: "node-detail", x: NODE_WIDTH / 2, y: NODE_HEIGHT - 13, "text-anchor": "middle" });
        const content = parts.join(" · ");
        detail.textContent = content.length > 35 ? `${content.slice(0, 33)}…` : content;
        group.append(detail);
      }
    } else if (node.children.length) {
      const badge = svgElement("text", { class: "node-count", x: NODE_WIDTH - 13, y: NODE_HEIGHT - 13, "text-anchor": "end" });
      badge.textContent = `${node.children.length} ${node.children.length === 1 ? "ruta" : "rutas"}`;
      group.append(badge);
    }

    group.addEventListener("click", () => selectNode(node));
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectNode(node);
      }
    });
    node.element = group;
    return group;
  }

  function renderEdge(edge) {
    const startX = edge.from.x + NODE_WIDTH;
    const endX = edge.to.x;
    const midX = (startX + endX) / 2;
    const path = svgElement("path", {
      class: "tree-edge",
      d: `M ${startX} ${edge.from.y} C ${midX} ${edge.from.y}, ${midX} ${edge.to.y}, ${endX - 3} ${edge.to.y}`,
      "marker-end": "url(#arrowhead)",
    });
    edge.element = path;
    return path;
  }

  function renderMap() {
    if (!window.DECISION_TREE) throw new Error("No se encontraron los datos del árbol de decisiones.");
    const layout = layoutTree(window.DECISION_TREE);
    Object.assign(state, layout);
    elements.svg.setAttribute("viewBox", `0 0 ${state.width} ${state.height}`);
    elements.svg.setAttribute("width", state.width);
    elements.svg.setAttribute("height", state.height);
    elements.svg.style.width = `${state.width}px`;
    elements.svg.style.height = `${state.height}px`;

    const defs = svgElement("defs");
    const marker = svgElement("marker", { id: "arrowhead", markerWidth: 8, markerHeight: 8, refX: 7, refY: 4, orient: "auto", markerUnits: "strokeWidth" });
    marker.append(svgElement("path", { d: "M0,0 L8,4 L0,8 z", class: "arrow-fill" }));
    defs.append(marker);
    elements.svg.append(defs);

    const edgeLayer = svgElement("g", { "aria-hidden": "true" });
    state.edges.forEach((edge) => edgeLayer.append(renderEdge(edge)));
    elements.svg.append(edgeLayer);

    const nodeLayer = svgElement("g");
    state.nodes.forEach((node) => nodeLayer.append(renderNode(node)));
    elements.svg.append(nodeLayer);

    elements.headerCount.textContent = `${state.nodes.length} nodos · ${state.leaves} resultados`;
    elements.mapSummary.textContent = `${state.nodes.length} nodos conectados · ${state.depth} niveles · ${state.leaves} resultados`;
    elements.footerStats.textContent = `${state.nodes.length} nodos · ${state.leaves} resultados`;
    elements.loading.classList.add("is-hidden");
    updateZoom(0.72);
    requestAnimationFrame(centerRoot);
  }

  function getAncestors(node) {
    const ancestors = [];
    for (let current = node; current; current = current.parent) ancestors.unshift(current);
    return ancestors;
  }

  function selectNode(node) {
    state.selected = node;
    const ancestors = new Set(getAncestors(node));
    state.nodes.forEach((item) => {
      item.element.classList.toggle("is-selected", item === node);
      item.element.classList.toggle("is-on-path", ancestors.has(item));
      item.element.classList.toggle("is-dimmed", !ancestors.has(item));
    });
    state.edges.forEach((edge) => {
      edge.element.classList.toggle("is-on-path", ancestors.has(edge.from) && ancestors.has(edge.to));
      edge.element.classList.toggle("is-dimmed", !(ancestors.has(edge.from) && ancestors.has(edge.to)));
    });
    renderDetails(node);
  }

  function appendInfoRow(label, value) {
    const row = document.createElement("div");
    row.className = "info-row";
    const key = document.createElement("span");
    key.textContent = label;
    const content = document.createElement("strong");
    content.textContent = value;
    row.append(key, content);
    elements.detailInfo.append(row);
  }

  function renderDetails(node) {
    elements.detailEmpty.hidden = true;
    elements.detailContent.hidden = false;
    const kind = nodeKind(node);
    const type = kind === "result" ? "resultado" : kind === "branch" ? "opción" : kind === "start" ? "inicio" : "pregunta";
    elements.detailType.dataset.type = type;
    elements.detailType.textContent = type.toUpperCase();
    elements.detailTitle.textContent = node.data.valor;
    elements.detailBreadcrumb.replaceChildren();
    getAncestors(node).forEach((ancestor) => {
      const item = document.createElement("li");
      item.textContent = ancestor.data.valor;
      elements.detailBreadcrumb.append(item);
    });

    elements.detailInfo.replaceChildren();
    if (node.data.clave) appendInfoRow("Clave", node.data.clave);
    if (node.data.tipo_salida) appendInfoRow("Tipo de salida", node.data.tipo_salida);
    if (node.data.recomendacion) appendInfoRow("Recomendación", node.data.recomendacion);

    elements.detailChildren.replaceChildren();
    if (node.children.length) {
      const label = document.createElement("span");
      label.className = "detail-section-label";
      label.textContent = `SIGUIENTE PASO · ${node.children.length}`;
      const list = document.createElement("div");
      list.className = "detail-children-list";
      node.children.forEach((child) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "detail-child";
        const arrow = document.createElement("span");
        arrow.textContent = "↳";
        const text = document.createElement("span");
        text.textContent = child.data.valor;
        button.append(arrow, text);
        button.addEventListener("click", () => {
          selectNode(child);
          centerNode(child);
        });
        list.append(button);
      });
      elements.detailChildren.append(label, list);
    } else {
      const label = document.createElement("span");
      label.className = "detail-section-label";
      label.textContent = "FINAL DE ESTA RAMA";
      elements.detailChildren.append(label);
    }
  }

  function updateZoom(zoom, anchorX = null, anchorY = null) {
    const nextZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, zoom));
    const previous = state.zoom || nextZoom;
    const viewport = elements.viewport;
    const x = anchorX ?? viewport.clientWidth / 2;
    const y = anchorY ?? viewport.clientHeight / 2;
    const contentX = (viewport.scrollLeft + x) / previous;
    const contentY = (viewport.scrollTop + y) / previous;
    state.zoom = nextZoom;
    elements.svg.style.width = `${state.width * nextZoom}px`;
    elements.svg.style.height = `${state.height * nextZoom}px`;
    elements.zoomValue.textContent = `${Math.round(nextZoom * 100)}%`;
    if (anchorX !== null || anchorY !== null) {
      viewport.scrollLeft = contentX * nextZoom - x;
      viewport.scrollTop = contentY * nextZoom - y;
    }
  }

  function fitMap() {
    const padding = 36;
    const zoom = Math.min((elements.viewport.clientWidth - padding) / state.width, 1);
    updateZoom(Math.max(MIN_ZOOM, zoom));
    elements.viewport.scrollLeft = 0;
    centerRoot();
  }

  function centerRoot() {
    elements.viewport.scrollLeft = 0;
    elements.viewport.scrollTop = Math.max(0, state.root.y * state.zoom - elements.viewport.clientHeight / 2);
  }

  function centerNode(node) {
    elements.viewport.scrollLeft = Math.max(0, (node.x + NODE_WIDTH / 2) * state.zoom - elements.viewport.clientWidth / 2);
    elements.viewport.scrollTop = Math.max(0, node.y * state.zoom - elements.viewport.clientHeight / 2);
  }

  function searchTree() {
    const query = elements.search.value.trim().toLocaleLowerCase("es");
    state.matches = query ? state.nodes.filter((node) => {
      const searchable = `${node.data.valor} ${node.data.recomendacion || ""} ${node.data.tipo_salida || ""}`.toLocaleLowerCase("es");
      return searchable.includes(query);
    }) : [];
    state.matchIndex = state.matches.length ? 0 : -1;
    state.nodes.forEach((node) => node.element.classList.toggle("is-match", state.matches.includes(node)));
    elements.searchCount.textContent = state.matches.length ? `1 / ${state.matches.length}` : query ? "0 resultados" : "";
    if (state.matches.length) focusMatch(0);
  }

  function focusMatch(index) {
    if (!state.matches.length) return;
    state.matchIndex = (index + state.matches.length) % state.matches.length;
    const node = state.matches[state.matchIndex];
    elements.searchCount.textContent = `${state.matchIndex + 1} / ${state.matches.length}`;
    centerNode(node);
    node.element.classList.remove("is-search-current");
    requestAnimationFrame(() => node.element.classList.add("is-search-current"));
  }

  elements.search.addEventListener("input", searchTree);
  elements.searchPrev.addEventListener("click", () => focusMatch(state.matchIndex - 1));
  elements.searchNext.addEventListener("click", () => focusMatch(state.matchIndex + 1));
  elements.zoomOut.addEventListener("click", () => updateZoom(state.zoom - 0.1));
  elements.zoomIn.addEventListener("click", () => updateZoom(state.zoom + 0.1));
  elements.fitView.addEventListener("click", fitMap);
  elements.themeToggle.addEventListener("click", () => setTheme(document.body.dataset.theme !== "dark"));
  elements.viewport.addEventListener("wheel", (event) => {
    if (!event.ctrlKey && !event.metaKey) return;
    event.preventDefault();
    const bounds = elements.viewport.getBoundingClientRect();
    const direction = event.deltaY < 0 ? 0.08 : -0.08;
    updateZoom(state.zoom + direction, event.clientX - bounds.left, event.clientY - bounds.top);
  }, { passive: false });
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== elements.search && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();
      elements.search.focus();
    }
    if (event.key === "Escape" && document.activeElement === elements.search) {
      elements.search.value = "";
      searchTree();
      elements.search.blur();
    }
  });

  try {
    setTheme(localStorage.getItem("decision-map-theme") === "dark");
    renderMap();
  } catch (error) {
    elements.loading.textContent = error.message;
    elements.mapSummary.textContent = "No fue posible cargar el árbol de decisiones.";
    console.error(error);
  }
})();
