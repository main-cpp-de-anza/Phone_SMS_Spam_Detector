# Pill Control Typography Design

## Goal

Align every pill-shaped control with the bold, uppercase, monospaced visual language from the supplied reference while preserving the site’s existing color roles.

## Hero tag

`MAIN.CPP CLUB` becomes text-only. Its pill background, border, and rounded container are removed. The text remains terracotta, becomes uppercase, increases in size, and uses tracked monospace typography.

## Pill controls

The GitHub button, hero calls-to-action, preset controls, and Analyze Message button retain their existing filled or outlined color treatments. They adopt uppercase labels, the existing monospace font stack, stronger weight, increased letter spacing, and roomier horizontal/vertical padding inspired by the reference.

## Responsive behavior

Controls retain their existing flex and wrapping behavior. The preset controls may wrap naturally rather than reduce the requested type scale.

## Scope

Only the relevant markup labels and CSS rules in `website/static/index.html` and `website/static/style.css` change. Routes, JavaScript behavior, and colors remain unchanged.
