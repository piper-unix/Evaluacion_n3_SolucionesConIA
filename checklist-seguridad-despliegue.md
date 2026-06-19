# Checklist de Seguridad y Despliegue — IL3.5

## Contenedores e Infraestructura

- [ ] **Usuarios no-root**: Todos los contenedores ejecutan la aplicación con un usuario sin privilegios (UID 1001).
- [ ] **Red interna**: Solo Caddy expone puertos al host (80, 443). Backend, frontend y monitoreo están en red interna.
- [ ] **Límites de recursos**: CPU y memoria limitados por servicio en docker-compose.
- [ ] **Imágenes base oficiales**: python:3.11-slim, caddy:2-alpine (superficie de ataque reducida).
- [ ] **Secretos fuera de la imagen**: API key inyectada vía .env en runtime, no en build.

## Comunicaciones (HTTPS)

- [ ] **Caddy como proxy inverso**: Termina TLS, sirve HTTPS.
- [ ] **Cabeceras de seguridad**:
  - [ ] Strict-Transport-Security (HSTS)
  - [ ] X-Content-Type-Options (nosniff)
  - [ ] X-Frame-Options (DENY)
  - [ ] Referrer-Policy
  - [ ] Permissions-Policy (restringe APIs del navegador)
  - [ ] Content-Security-Policy
  - [ ] X-XSS-Protection
  - [ ] Cabecera Server eliminada (evita fingerprinting)

## Rate Limiting

- [ ] **Capa Caddy**: Rate limiting por IP (10 req/min a API, 30 req/min global).
- [ ] **Capa aplicación**: slowapi en FastAPI (10 req/min por IP).

## Mitigaciones OWASP LLM Top 10

| # | Riesgo | Mitigación Implementada |
|---|--------|------------------------|
| LLM01 | Prompt Injection | Detección de patrones de inyección + guardrails en system prompt |
| LLM02 | Insecure Output Handling | Sanitización de salida (RUT, datos sensibles) |
| LLM03 | Training Data Poisoning | No se entrena el modelo; API externa de OpenAI |
| LLM04 | Model Denial of Service | Rate limiting (Caddy + FastAPI), límite de 4000 caracteres |
| LLM05 | Supply Chain | Dependencias pinned en requirements.txt, imágenes oficiales |
| LLM06 | Sensitive Information Disclosure | Filtros de entrada (RUT, tarjetas, contraseñas) + sanitización de salida |
| LLM07 | Insecure Plugin Design | Herramientas con alcance limitado (solo datos del metro) |
| LLM08 | Excessive Agency | Herramientas acotadas, no ejecutan comandos ni acceden a red externa |
| LLM09 | Overreliance | Disclaimer en respuestas, transparencia en monitoreo |
| LLM10 | Model Theft | API key protegida, modelo no expuesto localmente |

## AWS Academy EC2

- [ ] **Security Group restrictivo**: Solo puertos 22, 80, 443.
- [ ] **Instancia t2.medium**: Suficiente para 4 contenedores (512MB + 256MB + límites).
- [ ] **Key pair**: Acceso SSH con clave privada (sin contraseñas).
- [ ] **Apagado de recursos**: `docker compose down` + Stop instance + End Lab.
- [ ] **IAM**: Uso del rol `LabRole` de AWS Academy (mínimos privilegios).

## Arquitectura de Seguridad

```
                         Internet
                            |
                       [Caddy:80/443]   ← Proxy TLS + Rate Limiting
                     /         |        \
                    /          |         \
           [Backend:8000] [Frontend:8501] [Monitoring:8502]
              (API)          (Chat UI)       (Dashboard)
           
           Todos en red interna docker — sin exposición directa
```

