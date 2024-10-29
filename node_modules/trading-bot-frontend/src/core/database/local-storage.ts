import { Encryption } from '../security/encryption';

class LocalStorageService {
  private static instance: LocalStorageService;
  private readonly prefix: string = 'trading_app_';
  private readonly sensitiveKeys = ['api_keys', 'user_credentials', 'session_data'];

  private constructor() {
    // Private constructor to enforce singleton
  }

  public static getInstance(): LocalStorageService {
    if (!LocalStorageService.instance) {
      LocalStorageService.instance = new LocalStorageService();
    }
    return LocalStorageService.instance;
  }

  /**
   * Sets an item in localStorage with optional encryption
   */
  public async setItem(key: string, value: any, encrypt: boolean = false): Promise<void> {
    try {
      const prefixedKey = this.prefix + key;
      const stringValue = JSON.stringify(value);

      if (encrypt || this.sensitiveKeys.includes(key)) {
        const encryptedValue = await Encryption.encrypt(
          stringValue,
          process.env.REACT_APP_STORAGE_KEY || 'default-storage-key'
        );
        localStorage.setItem(prefixedKey, encryptedValue);
      } else {
        localStorage.setItem(prefixedKey, stringValue);
      }
    } catch (error) {
      console.error(`Error setting localStorage item: ${key}`, error);
      throw new Error('Failed to store data');
    }
  }

  /**
   * Gets an item from localStorage with automatic decryption if needed
   */
  public async getItem<T>(key: string, decrypt: boolean = false): Promise<T | null> {
    try {
      const prefixedKey = this.prefix + key;
      const value = localStorage.getItem(prefixedKey);

      if (!value) return null;

      if (decrypt || this.sensitiveKeys.includes(key)) {
        const decryptedValue = await Encryption.decrypt(
          value,
          process.env.REACT_APP_STORAGE_KEY || 'default-storage-key'
        );
        return JSON.parse(decryptedValue);
      }

      return JSON.parse(value);
    } catch (error) {
      console.error(`Error getting localStorage item: ${key}`, error);
      throw new Error('Failed to retrieve data');
    }
  }

  /**
   * Removes an item from localStorage
   */
  public removeItem(key: string): void {
    const prefixedKey = this.prefix + key;
    localStorage.removeItem(prefixedKey);
  }

  /**
   * Clears all app-related items from localStorage
   */
  public clearAll(): void {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(this.prefix)) {
        localStorage.removeItem(key);
      }
    });
  }

  /**
   * Gets all keys stored by the application
   */
  public getAllKeys(): string[] {
    const keys = Object.keys(localStorage);
    return keys
      .filter(key => key.startsWith(this.prefix))
      .map(key => key.replace(this.prefix, ''));
  }

  /**
   * Checks if an item exists in localStorage
   */
  public hasItem(key: string): boolean {
    const prefixedKey = this.prefix + key;
    return localStorage.getItem(prefixedKey) !== null;
  }

  /**
   * Gets the storage usage information
   */
  public getStorageInfo(): { used: number; total: number; percentage: number } {
    const used = new Blob(Object.values(localStorage)).size;
    const total = 5 * 1024 * 1024; // 5MB typical localStorage limit
    return {
      used,
      total,
      percentage: (used / total) * 100
    };
  }

  /**
   * Backs up all data to a JSON string
   */
  public async backup(): Promise<string> {
    const backup: Record<string, any> = {};
    const keys = this.getAllKeys();

    for (const key of keys) {
      const value = await this.getItem(key);
      if (value !== null) {
        backup[key] = value;
      }
    }

    return JSON.stringify(backup);
  }

  /**
   * Restores data from a backup string
   */
  public async restore(backupString: string): Promise<void> {
    try {
      const backup = JSON.parse(backupString);
      
      // Clear existing data first
      this.clearAll();

      // Restore each item
      for (const [key, value] of Object.entries(backup)) {
        const shouldEncrypt = this.sensitiveKeys.includes(key);
        await this.setItem(key, value, shouldEncrypt);
      }
    } catch (error) {
      console.error('Error restoring backup:', error);
      throw new Error('Failed to restore backup');
    }
  }
}

// Export a singleton instance
export const localStorage = LocalStorageService.getInstance();

// Example usage:
// await localStorage.setItem('user_settings', { theme: 'dark' });
// const settings = await localStorage.getItem('user_settings');
// localStorage.removeItem('user_settings');