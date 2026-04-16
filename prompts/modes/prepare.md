# Modo: prepare — Paquete de preparación para entrevistas

## Objetivo

Generar un paquete completo de preparación para entrevistas basado en:

- El rol y la empresa mencionados en la petición
- El contenido de `cv.md`
- El contenido de `config/profile.yml`
- El contenido de `article-digest.md` si existe

El entregable debe ser un prep pack claro y accionable que incluya preguntas probables, respuestas alineadas con la experiencia real del candidato, riesgos, y consejos para el día de la entrevista.

## Pipeline

1. Detectar la empresa, el título del rol y el tipo de entrevista (phone screen, technical screen, interview prep, etc.) de la petición del usuario.
2. Confirmar si la petición pide un PDF o un documento para imprimir. Si lo pide explícitamente, generar un archivo HTML y convertirlo a PDF usando `node generate-pdf.mjs`.
3. Leer `cv.md`, `config/profile.yml` y `article-digest.md`.
4. No inventar experiencia ni métricas. Si hay contenido incierto en la petición del usuario (por ejemplo, "sales for certification"), aclarar la narrativa y recomendar la forma correcta de presentarlo: honestamente, enfocado en el rol real, sin exagerar.
5. Construir el paquete de preparación con estas secciones:
   - Resumen corto del rol y por qué el candidato es un buen ajuste.
   - 6-8 preguntas más probables (comportamentales + técnicas/rol específicas).
   - Respuestas o guiones de respuesta basados en la experiencia real del candidato.
   - 3-4 preguntas "red-flag" y cómo responderlas.
   - Consejos de preparación del día de la entrevista.
   - Si hay un detalle de entrevista técnico, incluir una breve guía de cómo estructurar la respuesta.
6. Si hay una empresa objetivo claramente identificada, guardar el archivo como `output/interview-prep-{company-slug}-{YYYY-MM-DD}.md`. Si la petición pide PDF, también generar `output/interview-prep-{company-slug}-{YYYY-MM-DD}.pdf`.

## Reglas

- Siempre usar el lenguaje del usuario (EN/ES) si se puede inferir.
- Si el usuario menciona una corrección específica de la carta de presentación, ajustar la narrativa para que sea veraz y relevante.
- No presentar la preparación como "solo practica"; presentar recomendaciones concretas (qué puntos enfatizar, qué experiencias destacar).
- Para cada pregunta, usar un formato claro: pregunta + respuesta / bullet points.
- Si se genera PDF, informar la ruta de salida exacta.

## Entregable mínimo

- Título del documento: `Interview Prep — {Company} — {Role}`
- Sección 1: Por qué encajas con este rol
- Sección 2: Preguntas probables y respuestas
- Sección 3: Preguntas red-flag y respuestas
- Sección 4: Consejos de entrevista
- Sección 5: Qué corregir o aclarar en tu narrativa actual

## Instrucciones de conversión a PDF

Si el usuario pide un PDF explícito:

1. Generar HTML limpio con el contenido del paquete de preparación.
2. Guardar el HTML en `/tmp/interview-prep-{company-slug}-{YYYY-MM-DD}.html` o `output/interview-prep-{company-slug}-{YYYY-MM-DD}.html`.
3. Ejecutar:

   ```bash
   node generate-pdf.mjs /tmp/interview-prep-{company-slug}-{YYYY-MM-DD}.html output/interview-prep-{company-slug}-{YYYY-MM-DD}.pdf --format=a4
   ```

4. Responder con la ruta del PDF generado y sugerir abrirlo para revisión.

## Nombres de archivos

- Markdown: `output/interview-prep-{company-slug}-{YYYY-MM-DD}.md`
- HTML intermedio: `output/interview-prep-{company-slug}-{YYYY-MM-DD}.html`
- PDF final: `output/interview-prep-{company-slug}-{YYYY-MM-DD}.pdf`
