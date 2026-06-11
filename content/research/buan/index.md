---
title: "Bundle Analytics (BUAN)"
role: "project"
weight: 1
tag: "Bundle Analytics"
summary: "A computational framework for investigating the shapes and along-tract profiles of white matter pathways across populations."
showDate: false
showAuthor: false
showReadingTime: false
showWordCount: false
showPagination: false
---

**BUAN (Bundle Analytics)** is an open-source computational framework for population-level statistical analysis of white matter fiber bundle shapes and along-tract scalar profiles from diffusion MRI. It enables researchers to detect, localize, and visualize subtle white matter differences across large cohorts — bridging the gap between raw tractography data and interpretable neuroscientific findings.

## The Problem

Standard diffusion MRI analyses collapse rich 3D white matter information into single scalar summaries per tract, discarding the spatial variation that carries the most biologically meaningful signal. BUAN was designed to preserve and exploit this along-tract variation — enabling detection of localized group differences that global metrics would miss entirely.

## Framework Overview

BUAN operates as an end-to-end pipeline with four tightly integrated stages:

**1. Bundle Extraction**  
Fiber bundles are segmented from whole-brain tractography using atlas-based RecoBundles, producing subject-specific white matter tracts across 30+ anatomically defined pathways (e.g., corticospinal tract, arcuate fasciculus, inferior fronto-occipital fasciculus).

**2. Along-Tract Profiling**  
Each bundle is divided into **N** segments along its trajectory. Streamline points are assigned to segments based on their distance to the atlas bundle centroid, establishing anatomical correspondence across subjects, groups, and populations. At each point, scalar MRI metrics are sampled — including:
- **Fractional Anisotropy (FA)** — fiber organization and myelination
- **Mean Diffusivity (MD)** — overall water diffusion magnitude
- **Radial Diffusivity (RD)** — diffusion perpendicular to axons
- **Axial Diffusivity (AD)** — diffusion parallel to axons

**3. Shape Analysis**  
Bundle geometry is quantified using a streamline-based bundle adjacency metric, enabling comparison of tract shape across subjects and groups. Pairwise bundle similarities are used to construct a bundle-shape network that facilitates quality control and identification of anatomical outliers.

**4. Population-Level Statistics**  
Linear models and non-parametric tests are applied point-by-point along each bundle. Results are corrected for multiple comparisons and projected back onto the 3D tract geometry for direct anatomical visualization.

<div style="text-align:center; margin:1.5rem 0 0.5rem;">
  <img src="BUAN_Fig.png" style="width:95%; border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,0.1);">
  <p style="font-size:0.82rem; color:#666; margin:0.4rem 0 0;"><em>BUAN pipeline: atlas-based bundle extraction → along-tract scalar profiling via bundle assignment maps → population-level statistical comparison.</em></p>
</div>

## Applications

BUAN has been applied across a range of neurological and psychiatric conditions:

| Study | Finding |
|---|---|
| Alzheimer's Disease | Localized FA reductions in fornix and cingulum bundle |
| Parkinson's Disease | MD increases along the corticospinal tract |
| Mild Cognitive Impairment | Along-tract microstructural changes preceding diagnosis |
| Autism Spectrum Disorder | Commissural and association tract microstructural differences |
| Bipolar Disorder | Multi-site abnormalities along limbic tracts |

## Validation

BUAN was validated on the **Alzheimer's Disease Neuroimaging Initiative (ADNI)** dataset, demonstrating:
- Significantly higher statistical power than ROI-based and tract-averaged approaches
- Replication of known white matter pathology patterns in AD
- Consistent results across scanner sites after harmonization

## Publication

Chandio, B. Q., Risacher, S. L., Pestilli, F., Bullock, D., Yeh, F.-C., Koudoro, S., Rokem, A., Harezlak, J., & Garyfallidis, E. (2020). **Bundle analytics, a computational framework for investigating the shapes and profiles of brain pathways across populations.** *Scientific Reports*, 10, 17149. [https://doi.org/10.1038/s41598-020-74054-4](https://doi.org/10.1038/s41598-020-74054-4)

## Code & Integration

- **Bundle Shape Similarity Score:** [docs.dipy.org](https://docs.dipy.org/stable/examples_built/streamline_analysis/bundle_shape_similarity.html)
- **Bundle Assignment Maps Creation:** [docs.dipy.org](https://docs.dipy.org/stable/examples_built/streamline_analysis/bundle_assignment_maps.html)
- **Bundle Profiles:** [docs.dipy.org](https://docs.dipy.org/stable/examples_built/streamline_analysis/buan_bundle_profiles.html)
- **GitHub (DIPY):** [github.com/dipy/dipy](https://github.com/dipy/dipy)
- Fully open-source under BSD license — no commercial dependencies
