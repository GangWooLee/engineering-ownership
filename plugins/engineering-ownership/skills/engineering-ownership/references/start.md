# Start

1. Restore repository and ownership context.
2. Classify the highest applicable risk.
3. Choose a stable change ID and human-readable title.
4. For R1+, run:

   ```text
   engineering change start <id> --risk <R1|R2|R3> --title "<title>"
   ```

5. Fill the required Brief before implementation. For R2/R3, fill the ADR and
   operational records needed by the risk gate.
6. Link existing gstack, Superpowers, OpenSpec, or other planning/test artifacts
   rather than copying them.
7. Search existing responsibilities and record reuse or the reason not to
   reuse.
8. Implement in small reviewable units and update the decision record when the
   design actually changes.

If changed paths raise the risk, stop verification and run
`engineering change set-risk <id> --risk <higher-risk>`.
