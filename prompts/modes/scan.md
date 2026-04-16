# Modo: scan — Portal Scanner (Descubrimiento de Ofertas)

Escanea portales de empleo configurados, filtra por relevancia de título,
y añade nuevas ofertas al pipeline para evaluación posterior.

## Ejecución recomendada

Ejecutar como subagente para no consumir contexto del main:

```python
Agent(
    subagent_type="general-purpose",
    prompt="[contenido de este archivo + datos específicos]",
    run_in_background=True
)
```

## Configuración

Leer `portals.yml` que contiene:

- `search_queries`: Lista de queries WebSearch con `site:` filters por portal
- `tracked_companies_my` + `tracked_companies_global`: Empresas con `careers_url` para navegación directa
- `title_filter`: Keywords positive/negative/seniority_boost para filtrado de títulos

## Estrategia de descubrimiento (3 niveles)

### Nivel 1 — Playwright directo (PRINCIPAL)

Navegar a `careers_url` de cada empresa en `tracked_companies_my` +
`tracked_companies_global`. Más fiable — ve SPAs en tiempo real, no depende
de caché de Google. Cada empresa DEBE tener `careers_url`; si falta,
buscarla, guardarla.

### Nivel 2 — Greenhouse API (COMPLEMENTARIO)

Para empresas con campo `api:` en portals.yml. Más rápido que Playwright
pero solo Greenhouse.

Extraer: `{title, absolute_url as url, company}` — ver formato JSON completo
en Workflow paso 5.

### Nivel 3 — WebSearch queries (DESCUBRIMIENTO AMPLIO)

`search_queries` con `site:` filters. Útil para descubrir empresas NUEVAS
no en las listas de tracked; resultados pueden estar desfasados.

**Prioridad de ejecución:**

1. Nivel 1: Playwright → todas las empresas en `tracked_companies_my` + `tracked_companies_global` con `careers_url`
2. Nivel 2: API → todas las empresas en `tracked_companies_my` + `tracked_companies_global` con `api:`
3. Nivel 3: WebSearch → todos los `search_queries` con `enabled: true`

Los niveles son aditivos — se ejecutan todos, los resultados se mezclan y
deduplicar.

## Workflow

1. **Leer configuración**: `portals.yml`
2. **Leer historial**: `data/scan-history.tsv` → URLs ya vistas
3. **Leer dedup sources**: `data/applications.md` + `data/pipeline.md`

4. **Nivel 1 — Playwright scan** (paralelo en batches de 3-5):
   Para cada empresa en `tracked_companies_my` y `tracked_companies_global`
   con `enabled: true` y `careers_url` definida:
   - a. `browser_navigate` a la `careers_url`
   - b. `browser_snapshot` para leer todos los job listings
   - c. Si la página tiene filtros/departamentos, navegar las secciones relevantes
   - d. Para PAGINACIÓN: detectar botones "Next" o "Cargar más". Si existen,
     navegar hasta que no haya más resultados (max 10 páginas)
   - e. Para cada job listing extraer: `{title, url, company}`
   - f. Acumular en lista de candidatos
   - g. Si `careers_url` falla (404, redirect), intentar `scan_query` como
     fallback y anotar para actualizar la URL

5. **Nivel 2 — Greenhouse APIs** (paralelo):
   Para cada empresa en `tracked_companies_my` y `tracked_companies_global`
   con `api:` definida y `enabled: true`:
   - a. WebFetch de la URL de API: `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs`
   - b. Parsear JSON → extraer array `jobs`
   - c. Para cada job extraer: `{title, absolute_url as url, company}`
   - d. Acumular en lista de candidatos (dedup con Nivel 1)

6. **Nivel 3 — WebSearch queries** (paralelo si posible):
   Para cada query en `search_queries` con `enabled: true`:
   - a. Ejecutar WebSearch con el `query` definido
   - b. De cada resultado extraer: `{title, url, company, query_source}`
     - **query_source**: usar el campo `name` de la query en `search_queries`
     - **title**: del título del resultado (antes del " @ " o " | ")
     - **url**: URL del resultado
     - **company**: después del " @ " en el título, o extraer del dominio/path
   - c. Acumular en lista de candidatos (dedup con Nivel 1+2)

7. **Filtrar por título** usando `title_filter` de `portals.yml`:
   - Si la lista `positive` NO está vacía: al menos 1 keyword de `positive`
     DEBE aparecer en el título (case-insensitive, partial match)
   - Si la lista `positive` ESTÁ vacía: pasar todos sin filtro positivo
   - 0 keywords de `negative` deben aparecer (case-insensitive, partial match)
   - `seniority_boost` keywords: no son obligatorios, pero crean una columna
     "priority" (se muestran primero en el resumen final)

8. **Deduplicar** contra 3 fuentes (normalizar títulos: lowercase, trim,
   collapse whitespace):
   - `scan-history.tsv` → URL exacta ya vista
   - `applications.md` → empresa + rol normalizado ya evaluado
   - `pipeline.md` → URL exacta ya en pendientes o procesadas
   - Dedup entre niveles: si una URL aparece en Nivel 1 y Nivel 3,
     mantener solo Nivel 1 (más confiable)

9. **Para cada oferta nueva que pase filtros**:
   - a. Añadir a `pipeline.md` sección "Pendientes":
     `- [ ] {url} | {company} | {title}`
   - b. Registrar en `scan-history.tsv`:
     `{url}\t{date}\t{query_source}\t{title}\t{company}\tadded`

10. **Ofertas filtradas por título**: registrar en `scan-history.tsv` con
    status `skipped_title`
11. **Ofertas duplicadas**: registrar con status `skipped_dup`

## Extracción de título y empresa de WebSearch results

Los resultados de WebSearch vienen en formato: `"Job Title @ Company"` o
`"Job Title | Company"` o `"Job Title — Company"`.

Patrones de extracción por portal:

- **Ashby**: `"Senior AI PM (Remote) @ EverAI"` → title: `Senior AI PM`, company: `EverAI`
- **Greenhouse**: `"AI Engineer at Anthropic"` → title: `AI Engineer`, company: `Anthropic`
- **Lever**: `"Product Manager - AI @ Temporal"` → title: `Product Manager - AI`, company: `Temporal`

**Regex robusto:**

```text
(.+?)(?:\s*(?:@|at|—)\s*|\s+(?:at|in)\s+)(.+?)$
```

Lógica de extracción:

1. Buscar separador: `@`, `at`, `—` (en-dash), o ` at ` / ` in `
2. Todo antes del separador es el título (trim whitespace)
3. Todo después es la empresa (trim whitespace)
4. Si no hay separador claro, extraer empresa del dominio de la URL

## URLs privadas

Si se encuentra una URL no accesible públicamente:

1. Guardar el JD en `jds/{company}-{role-slug}.md`
2. Añadir a pipeline.md como: `- [ ] local:jds/{company}-{role-slug}.md | {company} | {title}`

## Scan History

`data/scan-history.tsv` trackea TODAS las URLs vistas:

```text
url    date          query_source       title            company  status
https://...  2026-02-10  Ashby — AI PM    Senior AI PM   Acme     added
https://...  2026-02-10  Greenhouse — BE  Junior Backend  BigCo    skipped_title
https://...  2026-02-10  Ashby — AI PM    Senior AI Eng  OldCo    skipped_dup
```

**Columnas (ORDEN IMPORTA):**

1. `url` — URL completa
2. `date` — YYYY-MM-DD cuando se vio primero
3. `query_source` — nombre de la query de `search_queries` o
   "Playwright — {company}" para Nivel 1
4. `title` — título exacto del job
5. `company` — empresa (normalizada: trim, lowercase)
6. `status` — `added`, `skipped_title`, `skipped_dup`

## Resumen de salida

```text
Portal Scan — {YYYY-MM-DD}
━━━━━━━━━━━━━━━━━━━━━━━━━━
Niveles ejecutados: 1 (Playwright) + 2 (APIs) + 3 (WebSearch)
Empresas escaneadas: N
Queries ejecutados: N
Ofertas encontradas: N total
├─ Relevantes por título: N
├─ Filtradas por título: N
└─ Duplicadas (ya evaluadas): N
Nuevas añadidas a pipeline.md: N

PRIORIDAD (con seniority_boost):
  ⭐ {company} | {title}
  ...

ESTÁNDAR:
  + {company} | {title}
  ...

→ Ejecuta /career-ops pipeline para evaluar las nuevas ofertas.
```

## Gestión de careers_url

Cada empresa en `tracked_companies_my` y `tracked_companies_global` debe
tener `careers_url` — la URL directa a su página de ofertas.

**Patrones conocidos por plataforma:**

- **Ashby:** `https://jobs.ashbyhq.com/{slug}`
- **Greenhouse:** `https://boards.greenhouse.io/{slug}` o
  `https://boards.eu.greenhouse.io/{slug}`
  (nota: para API usar `boards-api.greenhouse.io`)
- **Lever:** `https://jobs.lever.co/{slug}`
- **Custom:** La URL propia de la empresa (ej: `https://openai.com/careers`)

**Si `careers_url` no existe** para una empresa:

1. Intentar el patrón de su plataforma conocida
2. Si falla, hacer un WebSearch rápido: `"{company}" careers jobs`
3. Navegar con Playwright para confirmar que funciona
4. **Guardar la URL encontrada en portals.yml** para futuros scans

**Si `careers_url` devuelve 404 o redirect:**

1. Anotar en el resumen de salida: `⚠️ {company} careers URL needs update`
2. Intentar scan_query como fallback
3. Marcar para actualización manual en próximo ciclo

## Mantenimiento del portals.yml

- **SIEMPRE guardar `careers_url`** cuando se añade una empresa nueva
- Añadir nuevos queries según se descubran portales o roles interesantes
- Incluir field `name` en cada query (ej: `name: "Ashby — AI PM"`) para
  claridad en scan-history
- Desactivar queries con `enabled: false` si generan demasiado ruido
- Ajustar keywords de filtrado según evolucionen los roles target
- Añadir empresas a `tracked_companies_my` (Malaysia/APAC) o
  `tracked_companies_global` (AI-first/global) cuando interese seguirlas
- Verificar `careers_url` periódicamente — las empresas cambian de ATS
  cada año aprox.
