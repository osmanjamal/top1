/**
 * Utility class for handling encryption and decryption of sensitive data
 */
export class Encryption {
    private static readonly ALGORITHM = 'AES-GCM';
    private static readonly KEY_LENGTH = 256;
    private static readonly IV_LENGTH = 12;
    private static readonly SALT_LENGTH = 16;
    private static readonly ENCODING = 'base64';
  
    /**
     * Generates a cryptographic key from a password
     */
    private static async generateKey(password: string, salt: Uint8Array): Promise<CryptoKey> {
      const encoder = new TextEncoder();
      const passwordBuffer = encoder.encode(password);
  
      const keyMaterial = await crypto.subtle.importKey(
        'raw',
        passwordBuffer,
        'PBKDF2',
        false,
        ['deriveKey']
      );
  
      return crypto.subtle.deriveKey(
        {
          name: 'PBKDF2',
          salt,
          iterations: 100000,
          hash: 'SHA-256'
        },
        keyMaterial,
        { name: this.ALGORITHM, length: this.KEY_LENGTH },
        true,
        ['encrypt', 'decrypt']
      );
    }
  
    /**
     * Encrypts sensitive data
     */
    public static async encrypt(data: string, password: string): Promise<string> {
      try {
        const encoder = new TextEncoder();
        const salt = crypto.getRandomValues(new Uint8Array(this.SALT_LENGTH));
        const iv = crypto.getRandomValues(new Uint8Array(this.IV_LENGTH));
        const key = await this.generateKey(password, salt);
  
        const encryptedData = await crypto.subtle.encrypt(
          {
            name: this.ALGORITHM,
            iv
          },
          key,
          encoder.encode(data)
        );
  
        // Combine salt, iv, and encrypted data
        const resultBuffer = new Uint8Array(
          salt.length + iv.length + new Uint8Array(encryptedData).length
        );
        resultBuffer.set(salt, 0);
        resultBuffer.set(iv, salt.length);
        resultBuffer.set(new Uint8Array(encryptedData), salt.length + iv.length);
  
        return btoa(String.fromCharCode(...resultBuffer));
      } catch (error) {
        console.error('Encryption failed:', error);
        throw new Error('Failed to encrypt data');
      }
    }
  
    /**
     * Decrypts encrypted data
     */
    public static async decrypt(encryptedData: string, password: string): Promise<string> {
      try {
        const decoder = new TextDecoder();
        const dataBuffer = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
  
        const salt = dataBuffer.slice(0, this.SALT_LENGTH);
        const iv = dataBuffer.slice(this.SALT_LENGTH, this.SALT_LENGTH + this.IV_LENGTH);
        const data = dataBuffer.slice(this.SALT_LENGTH + this.IV_LENGTH);
  
        const key = await this.generateKey(password, salt);
  
        const decryptedData = await crypto.subtle.decrypt(
          {
            name: this.ALGORITHM,
            iv
          },
          key,
          data
        );
  
        return decoder.decode(decryptedData);
      } catch (error) {
        console.error('Decryption failed:', error);
        throw new Error('Failed to decrypt data');
      }
    }
  
    /**
     * Hashes sensitive data (e.g., for API keys)
     */
    public static async hash(data: string): Promise<string> {
      const encoder = new TextEncoder();
      const dataBuffer = encoder.encode(data);
      const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    }
  
    /**
     * Generates a secure random string
     */
    public static generateRandomString(length: number = 32): string {
      const array = new Uint8Array(length);
      crypto.getRandomValues(array);
      return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }
  }
  
  export const encryptApiKey = async (apiKey: string): Promise<string> => {
    const password = process.env.REACT_APP_ENCRYPTION_KEY || 'default-encryption-key';
    return Encryption.encrypt(apiKey, password);
  };
  
  export const decryptApiKey = async (encryptedApiKey: string): Promise<string> => {
    const password = process.env.REACT_APP_ENCRYPTION_KEY || 'default-encryption-key';
    return Encryption.decrypt(encryptedApiKey, password);
  };