/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_AUTO_SAVE_INTERVAL: string;
  readonly VITE_LOCAL_BACKUP_ENABLED: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
