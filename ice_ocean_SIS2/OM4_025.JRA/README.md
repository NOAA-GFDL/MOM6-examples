Todo:
- JRA variables appear to not be at 10m in atmosphere?
  - Variable "height" in JRA files = 10m implying variables are indeed 10m atmospheric variables
- Use ts or tas?
  - tas is t_10. ts is brightness temp.
- With CORE we use q_10_mod which was an adjustment to q_10.
- NCAR precip/snow were scaled by 0.9933
  - Assuming this was a tuning to bring freshwater budget to balaance. Setting to 1.
