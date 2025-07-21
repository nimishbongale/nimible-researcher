![Mermaid Chart - Create complex, visual diagrams with text  A smarter way of creating diagrams -2025-07-06-152058](https://github.com/user-attachments/assets/4f7dcd6e-3e90-44a7-86de-70664225e97e)---
title: Nimible Researcher V4
emoji: 👁
colorFrom: yellow
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: Agentic Deep Research!
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Notes

## Agents

1. Problem framer (rewrite succint) (llama 70B, best understanding) (meta-llama/Llama-3.3-70B-Instruct-Turbo-Free)
2. Retriver agent (RAG + Web Search) (Can be a tiny model, just calls tools/RAG, explore) (lgai/exaone-3-5-32b-instruct)
3. Critic (Validator) (reasoning model with a custom prompt, perhaps lgai deep does the trick) (deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free)
4. Compressor (TL;DR agent) (needs large context, good number of output tokens) (lgai/exaone-deep-32b) 
5. Writer (large context, final result) (lgai/exaone-3-5-32b-instruct)

## Questions

1. May need an orchaestor perhaps, but will using sequential for now to save tokens
2. Just use a sequential agent with known handoffs

## Options

lgai/exaone-3-5-32b-instruct
deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free
lgai/exaone-deep-32b
meta-llama/Llama-3.3-70B-Instruct-Turbo-Free

![Uploading Mermaid Chart - Create c<svg id="export-svg" width="100%" xmlns="http://www.w3.org/2000/svg" class="flowchart" style="max-width: 1007.84375px;" viewBox="0 0 1007.84375 745" role="graphics-document document" aria-roledescription="flowchart-v2"><style xmlns="http://www.w3.org/1999/xhtml">/* Copyright 2019 The Recursive Project Authors (github.com/arrowtype/recursive)
