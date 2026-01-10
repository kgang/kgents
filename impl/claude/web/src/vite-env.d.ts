/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_WS_URL: string;
  readonly VITE_STRIPE_PUBLISHABLE_KEY: string;
  readonly VITE_AUTH_PROVIDER: string;
  /** Set to 'true' to disable the witness stream (useful when backend is not running) */
  readonly VITE_DISABLE_WITNESS_STREAM: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
