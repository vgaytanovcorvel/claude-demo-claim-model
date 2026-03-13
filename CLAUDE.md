# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A small React + TypeScript app that demonstrates the **claim model** concept through step-by-step infographic-style screens. Users navigate through sequential screens that visually explain the claim model.

## Commands

- `npm run dev` — start development server (Vite)
- `npm run build` — production build
- `npm run preview` — preview production build locally
- `npm run lint` — run ESLint

## Architecture

- **React + TypeScript** with Vite as the build tool
- Step-based navigation: the app presents a sequence of screens (steps) that the user advances through
- Each step is a self-contained visual/infographic component
