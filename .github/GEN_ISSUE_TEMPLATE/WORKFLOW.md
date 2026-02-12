# EMD Registration Workflow

## Submission Pipeline

![EMD Workflow](https://mermaid.ink/svg/pako:eNq9Vgtv2jAQ_iuWUacNJTySAG2kbep4tRJoVWGbtjEhkxhi1bGjxGlLH_995wRYWlrWVt0sJbF9r893vtxdY0_6FLt4zuWFF5BYocHpRKBs7O2ho-P-0QCeMTpEo_Fhv-uidkDEgiIVUJSoJaeIqGwxk0rJECmJArYIODyqoOhzpJgUiYtGiixo3ci_loGGvdXcXn0dLbWWTNLZIiZRsBL7OcHlcjZF9XJ5gn-t-fQYaXI_Zj5qU84T9AaNtDTzC3xU-I-rtwrqrS31Pouppw-Bxp_umLUIyB3JmF1JoQhH_bsmc54Z8HylsWLeNsdjoIa9DNAQIsRRj4SML5-MqjsagnAXAgqHWyaKhisN9-Tb2kZbhpEUVKhtnp0OswsOs7fjock5-I2Bp2p2Cpqdbc3OWvPj-kZ1ZJofbhalUslACbxvdKQ2VItkZC8n2H_2Z9n--f19O2eXYs4W6LgDNGdNA1cjswLUeeY8k_lFaru3TbSLQD3OvDMNd4IDpaLErVYXTAXprOLJsPqtfXpitofHJ9VukoADGeFmdnKzI700hB2io19lSZLSpCroxUeIdcSJou_13Z96kAtTIvxpkidDZRmC19B0xok4u4cBnPLqIIJNYkxBVZTmrLD6K5jZ64M5X2XgM6HYr48k1HwZjCwvdll3_pH1HTb1lf5HR87zYIdtSJj_a7pQpTrd3uGXwRhK3fdBd7T5NWVlLq9AsIjlGXVLtm0b-dy8YL4KXCu6NOaMc1dARB8QtV4kOuy93KL9clHnGaIPtgsm6vpMNwYsQZwJqvsCL-8cNu0Begtx1YFDMlVoLmMkCs3Du53ur9WaTc-7i8wuIsMGDmkcEuZDd3Od4cTQpoR0gl2Y-nROUg71aCJugZWkSo6WwsOuilNq4FimiwC7c8ITWKWRD7eowwhUqHCzq_8aG36oPjRuy1Qo7DbqBo6I-CFluKbDErvX-BK7VrNiW61GrdWyWlbTqrdsAy9hu7ZfaTkHMGp2w2k2Dhq3Br7KNNQq-62GgSn4U8bDvF3Lurbb3ySwHI0)

## Quick Reference

| Stage | Form | Creates | ID Format | Used By |
|-------|------|---------|-----------|---------|
| 1 | [Grid Cells & Subgrid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=grid_cell_and_subgrid.yml) | grid_cells + subgrid | g###, s### | Stage 2a |
| 2a | [Horizontal Grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=horizontal_computational_grid.yml) | horizontal_computational_grid | c### | Stage 3 |
| 2b | [Vertical Grid](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=vertical_computational_grid.yml) | vertical_computational_grid | v### | Stage 3 |
| 3 | [Model Component](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_component.yml) | component + component_config | {domain}_{name}_{c###}_{v###} | Stage 4 |
| 4 | [Model](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model.yml) | model | source_id | CMIP |
| — | [Model Family](https://github.com/WCRP-CMIP/Essential-Model-Documentation/issues/new?template=model_family.yml) | model_family | family-id | Stage 3/4 |

---

## Mermaid.ink URLs

Stage-highlighted diagrams for each template:

| Template | URL |
|----------|-----|
| Stage 1 (Grid Cells) | `https://mermaid.ink/svg/pako:eNq9Vgtv2jAQ...53ur9WaTc...` |
| Stage 2 (Horizontal/Vertical) | `https://mermaid.ink/svg/pako:eNq9Vgtv2jAQ...4d8uKkCa...` |
| Stage 3 (Model Component) | `https://mermaid.ink/svg/pako:eNq9Vgtv2jAQ...50nqtWaTc...` |
| Model Family | `https://mermaid.ink/svg/pako:eNq9Vgtv2jAQ...OWGqw` |
| Stage 4 (Model) | `https://mermaid.ink/svg/pako:eNq9Vgtv2jAQ...52warVm0...` |

Full URLs are stored in `_workflow_images.py`.
