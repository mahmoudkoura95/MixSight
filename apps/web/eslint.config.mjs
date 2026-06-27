// Minimal flat config. eslint-config-next + FlatCompat hit a circular-ref
// serialization bug under pnpm+ESLint 9; we rely on `tsc --noEmit` + the
// Next.js compiler for the bulk of static analysis. Expand this when a
// specific lint rule earns its keep.
export default [
  {
    ignores: [".next/**", "node_modules/**", "next-env.d.ts"],
  },
];
