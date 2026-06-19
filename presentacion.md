# IL3.5: Ciberseguridad y Despliegue en AWS

## Agente Inteligente del Metro de Santiago

---

## Arquitectura de Despliegue

```
                         Internet
                            |
                       [Caddy:80/443]
                     /         |        \
                    /          |         \
           [Backend:8000] [Frontend:8501] [Monitoring:8502]
              (API)          (Chat UI)       (Dashboard)
           
           Todos en red interna — solo Caddy expone puertos
```

---

## Contenerización Segura

| Medida | Implementación |
|--------|----------------|
| Usuario no-root | `appuser` (UID 1001) en todos los contenedores |
| Imágenes mínimas | `python:3.11-slim`, `caddy:2-alpine` |
| Recursos limitados | CPU y memoria acotados por servicio |
| Secretos en runtime | API key vía `.env`, no en la imagen |

---

## HTTPS y Cabeceras de Seguridad

**Caddy** maneja TLS automáticamente con `tls internal` (self-signed).

Cabeceras aplicadas:
- `Strict-Transport-Security` (HSTS preload)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy` restringida
- `Permissions-Policy` (sin cámaras, micrófono, geolocalización)
- `X-XSS-Protection: 1; mode=block`
- Cabecera `Server` eliminada

---

## Rate Limiting

| Capa | Límite | Herramienta |
|------|--------|-------------|
| Proxy (Caddy) | 10 req/min a API, 30 req/min global | `rate_limit` |
| Aplicación (FastAPI) | 10 req/min por IP | `slowapi` |

---

## OWASP LLM Top 10 — Mitigaciones

| # | Riesgo | Mitigación |
|---|--------|------------|
| 01 | Prompt Injection | Patrones de detección + guardrails en system prompt |
| 02 | Insecure Output | Sanitización de salida (RUT, datos personales) |
| 04 | Model DoS | Rate limiting + límite de 4000 caracteres |
| 06 | Info Disclosure | Filtros en entrada y salida |
| 08 | Excessive Agency | Herramientas acotadas al dominio del metro |

---

## Seguridad en AWS

- **Security Group**: Solo puertos 22 (SSH), 80 (HTTP), 443 (HTTPS)
- **IAM**: Rol `LabRole` de AWS Academy (privilegios mínimos)
- **Instancia**: `t2.medium` con 20 GB EBS
- **Key pair**: Autenticación SSH con clave privada

---

## Apagado de Recursos

1. `docker compose -f deploy/docker-compose.prod.yml down`
2. EC2: Stop instance (o Terminate si ya no aplica)
3. AWS Academy Lab: **End Lab**

> ⚠️ Los créditos son limitados. Apagar siempre al terminar.

---

## Demo

### Pruebas de seguridad:
1. Consultas normales (tarifa, ruta, impedimentos)
2. Prompt injection (intento de cambio de instrucciones)
3. Datos sensibles (RUT, contraseñas)
4. Rate limiting (peticiones consecutivas)
5. Cabeceras de seguridad HTTP

### URLs:
- Chat: `http://IP_PUBLICA`
- Monitoreo: `http://IP_PUBLICA/monitoring`
- Health: `http://IP_PUBLICA/api/health`

---

## Checklist Final

- [ ] Contenedores construidos y corriendo
- [ ] HTTPS funcionando (Caddy)
- [ ] Cabeceras de seguridad verificadas
- [ ] Rate limiting probado
- [ ] Prompt injection bloqueado
- [ ] Datos sensibles filtrados
- [ ] Recursos apagados al finalizar
