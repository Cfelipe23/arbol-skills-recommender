window.DECISION_TREE = {
  "valor": "Recomendador de Skills y Prompts",
  "hijos": [
    {
      "valor": "¿Cuál es tu perfil?",
      "clave": "perfil",
      "hijos": [
        {
          "valor": "Estoy aprendiendo / no sé qué lleva una aplicación por dentro",
          "clave": "perfil_basico",
          "hijos": [
            {
              "valor": "¿Dónde se va a desplegar?",
              "clave": "despliegue",
              "hijos": [
                {
                  "valor": "Móvil / Tablet",
                  "clave": "movil",
                  "hijos": [
                    {
                      "valor": "¿Es personal o empresarial?",
                      "clave": "tipo_app",
                      "hijos": [
                        {
                          "valor": "Personal / Proyecto pequeño",
                          "clave": "personal",
                          "tipo_salida": "prompt",
                          "recomendacion": "prompt_movil_personal"
                        },
                        {
                          "valor": "Empresarial",
                          "clave": "empresarial",
                          "hijos": [
                            {
                              "valor": "¿Cuántos usuarios estimas?",
                              "clave": "usuarios",
                              "hijos": [
                                {
                                  "valor": "10 a 100",
                                  "clave": "usuarios_bajo",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_movil_empresarial_bajo"
                                },
                                {
                                  "valor": "100 a 1000",
                                  "clave": "usuarios_medio",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_movil_empresarial_medio"
                                },
                                {
                                  "valor": "Más de 1000",
                                  "clave": "usuarios_alto",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_movil_empresarial_alto"
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "valor": "Web",
                  "clave": "web",
                  "hijos": [
                    {
                      "valor": "¿Es personal o empresarial?",
                      "clave": "tipo_app",
                      "hijos": [
                        {
                          "valor": "Personal / Proyecto pequeño",
                          "clave": "personal",
                          "tipo_salida": "prompt",
                          "recomendacion": "prompt_web_personal"
                        },
                        {
                          "valor": "Empresarial",
                          "clave": "empresarial",
                          "hijos": [
                            {
                              "valor": "¿Cuántos usuarios estimas?",
                              "clave": "usuarios",
                              "hijos": [
                                {
                                  "valor": "10 a 100",
                                  "clave": "usuarios_bajo",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_web_empresarial_bajo"
                                },
                                {
                                  "valor": "100 a 1000",
                                  "clave": "usuarios_medio",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_web_empresarial_medio"
                                },
                                {
                                  "valor": "Más de 1000",
                                  "clave": "usuarios_alto",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_web_empresarial_alto"
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "valor": "Escritorio",
                  "clave": "escritorio",
                  "hijos": [
                    {
                      "valor": "¿Es personal o empresarial?",
                      "clave": "tipo_app",
                      "hijos": [
                        {
                          "valor": "Personal / Proyecto pequeño",
                          "clave": "personal",
                          "tipo_salida": "prompt",
                          "recomendacion": "prompt_escritorio_personal"
                        },
                        {
                          "valor": "Empresarial",
                          "clave": "empresarial",
                          "hijos": [
                            {
                              "valor": "¿Cuántos usuarios estimas?",
                              "clave": "usuarios",
                              "hijos": [
                                {
                                  "valor": "10 a 100",
                                  "clave": "usuarios_bajo",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_escritorio_empresarial_bajo"
                                },
                                {
                                  "valor": "100 a 1000",
                                  "clave": "usuarios_medio",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_escritorio_empresarial_medio"
                                },
                                {
                                  "valor": "Más de 1000",
                                  "clave": "usuarios_alto",
                                  "tipo_salida": "prompt",
                                  "recomendacion": "prompt_escritorio_empresarial_alto"
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          "valor": "Soy desarrollador y necesito algo puntual",
          "clave": "perfil_experto",
          "hijos": [
            {
              "valor": "¿Qué área necesitas?",
              "clave": "area",
              "hijos": [
                {
                  "valor": "Backend / API / Base de Datos",
                  "clave": "backend_general",
                  "hijos": [
                    {
                      "valor": "¿Qué arquitectura o patrón estás utilizando?",
                      "clave": "arquitectura",
                      "hijos": [
                        {
                          "valor": "Clean / Hexagonal Architecture",
                          "clave": "arq_clean",
                          "hijos": [
                            {
                              "valor": "¿Qué tarea específica?",
                              "clave": "tarea",
                              "hijos": [
                                {
                                  "valor": "Diseñar endpoints REST",
                                  "clave": "endpoints_rest",
                                  "tipo_salida": "skill",
                                  "recomendacion": "rest-api-design"
                                },
                                {
                                  "valor": "Autenticación y seguridad",
                                  "clave": "auth",
                                  "tipo_salida": "skill",
                                  "recomendacion": "auth-security"
                                },
                                {
                                  "valor": "Diseño de esquema de BD",
                                  "clave": "esquema",
                                  "tipo_salida": "skill",
                                  "recomendacion": "db-schema-design"
                                },
                                {
                                  "valor": "Optimización de queries",
                                  "clave": "optimizacion",
                                  "tipo_salida": "skill",
                                  "recomendacion": "postgres-optimization"
                                }
                              ]
                            }
                          ]
                        },
                        {
                          "valor": "Microservicios",
                          "clave": "arq_microservicios",
                          "hijos": [
                            {
                              "valor": "¿Qué tarea específica?",
                              "clave": "tarea",
                              "hijos": [
                                {
                                  "valor": "Diseñar endpoints REST",
                                  "clave": "endpoints_rest",
                                  "tipo_salida": "skill",
                                  "recomendacion": "rest-api-design"
                                },
                                {
                                  "valor": "Integración y eventos",
                                  "clave": "integracion",
                                  "tipo_salida": "skill",
                                  "recomendacion": "service-integration"
                                },
                                {
                                  "valor": "Contenedores y despliegue",
                                  "clave": "contenedores",
                                  "tipo_salida": "skill",
                                  "recomendacion": "containers"
                                }
                              ]
                            }
                          ]
                        },
                        {
                          "valor": "Monolito Modular / Estándar",
                          "clave": "arq_monolito",
                          "hijos": [
                            {
                              "valor": "¿Qué tarea específica?",
                              "clave": "tarea",
                              "hijos": [
                                {
                                  "valor": "Diseñar endpoints REST",
                                  "clave": "endpoints_rest",
                                  "tipo_salida": "skill",
                                  "recomendacion": "rest-api-design"
                                },
                                {
                                  "valor": "Optimización del backend",
                                  "clave": "optimizacion",
                                  "tipo_salida": "skill",
                                  "recomendacion": "backend-optimization"
                                },
                                {
                                  "valor": "Migraciones y modelado",
                                  "clave": "modelado",
                                  "tipo_salida": "skill",
                                  "recomendacion": "data-modeling"
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    }
                  ]
                },
                {
                  "valor": "Frontend y UI",
                  "clave": "frontend",
                  "hijos": [
                    {
                      "valor": "¿Qué tarea específica?",
                      "clave": "tarea",
                      "hijos": [
                        {
                          "valor": "Crear componentes",
                          "clave": "crear_componentes",
                          "tipo_salida": "skill",
                          "recomendacion": "react-best-practices"
                        },
                        {
                          "valor": "Optimizar rendimiento",
                          "clave": "optimizar_rendimiento",
                          "tipo_salida": "skill",
                          "recomendacion": "frontend-performance"
                        },
                        {
                          "valor": "Accesibilidad (a11y)",
                          "clave": "accesibilidad",
                          "tipo_salida": "skill",
                          "recomendacion": "a11y-best-practices"
                        },
                        {
                          "valor": "Testing de UI",
                          "clave": "testing_ui",
                          "tipo_salida": "skill",
                          "recomendacion": "ui-testing"
                        }
                      ]
                    }
                  ]
                },
                {
                  "valor": "DevOps, QA y Seguridad",
                  "clave": "devops_qa",
                  "hijos": [
                    {
                      "valor": "¿Qué tarea específica?",
                      "clave": "tarea",
                      "hijos": [
                        {
                          "value": "CI/CD Pipelines",
                          "valor": "CI/CD Pipelines",
                          "clave": "cicd",
                          "tipo_salida": "skill",
                          "recomendacion": "cicd-pipeline"
                        },
                        {
                          "valor": "Tests unitarios y de integración",
                          "clave": "unitarios",
                          "tipo_salida": "skill",
                          "recomendacion": "unit-testing"
                        },
                        {
                          "valor": "OWASP y revisión de seguridad",
                          "clave": "owasp",
                          "tipo_salida": "skill",
                          "recomendacion": "revisor-seguridad"
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
};
