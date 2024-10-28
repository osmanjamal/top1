class IndexedDBService {
    private static instance: IndexedDBService;
    private readonly dbName = 'TradingAppDB';
    private readonly version = 1;
    private db: IDBDatabase | null = null;
  
    private readonly stores = {
      tradingHistory: 'tradingHistory',
      marketData: 'marketData',
      userSettings: 'userSettings',
      cachedData: 'cachedData'
    };
  
    private constructor() {
      this.initDatabase();
    }
  
    public static getInstance(): IndexedDBService {
      if (!IndexedDBService.instance) {
        IndexedDBService.instance = new IndexedDBService();
      }
      return IndexedDBService.instance;
    }
  
    /**
     * Initializes the database and creates object stores
     */
    private async initDatabase(): Promise<void> {
      return new Promise((resolve, reject) => {
        const request = indexedDB.open(this.dbName, this.version);
  
        request.onerror = () => {
          console.error('Error opening database');
          reject(request.error);
        };
  
        request.onsuccess = () => {
          this.db = request.result;
          resolve();
        };
  
        request.onupgradeneeded = (event) => {
          const db = (event.target as IDBOpenDBRequest).result;
  
          // Create Trading History store
          if (!db.objectStoreNames.contains(this.stores.tradingHistory)) {
            const tradingStore = db.createObjectStore(this.stores.tradingHistory, { keyPath: 'id' });
            tradingStore.createIndex('timestamp', 'timestamp');
            tradingStore.createIndex('symbol', 'symbol');
            tradingStore.createIndex('type', 'type');
          }
  
          // Create Market Data store
          if (!db.objectStoreNames.contains(this.stores.marketData)) {
            const marketStore = db.createObjectStore(this.stores.marketData, { keyPath: 'id' });
            marketStore.createIndex('symbol', 'symbol');
            marketStore.createIndex('timestamp', 'timestamp');
          }
  
          // Create User Settings store
          if (!db.objectStoreNames.contains(this.stores.userSettings)) {
            db.createObjectStore(this.stores.userSettings, { keyPath: 'key' });
          }
  
          // Create Cached Data store
          if (!db.objectStoreNames.contains(this.stores.cachedData)) {
            const cacheStore = db.createObjectStore(this.stores.cachedData, { keyPath: 'key' });
            cacheStore.createIndex('timestamp', 'timestamp');
          }
        };
      });
    }
  
    /**
     * Ensures database connection is ready
     */
    private async ensureConnection(): Promise<void> {
      if (!this.db) {
        await this.initDatabase();
      }
    }
  
    /**
     * Adds an item to a store
     */
    public async add<T>(storeName: string, item: T): Promise<IDBValidKey> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.add(item);
  
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Gets an item from a store by its key
     */
    public async get<T>(storeName: string, key: IDBValidKey): Promise<T | null> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.get(key);
  
        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Updates an item in a store
     */
    public async update<T>(storeName: string, item: T): Promise<void> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.put(item);
  
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Deletes an item from a store
     */
    public async delete(storeName: string, key: IDBValidKey): Promise<void> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.delete(key);
  
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Gets all items from a store
     */
    public async getAll<T>(storeName: string): Promise<T[]> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const request = store.getAll();
  
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Clears all data from a store
     */
    public async clearStore(storeName: string): Promise<void> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readwrite');
        const store = transaction.objectStore(storeName);
        const request = store.clear();
  
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Gets items by an index
     */
    public async getByIndex<T>(
      storeName: string,
      indexName: string,
      value: any
    ): Promise<T[]> {
      await this.ensureConnection();
      return new Promise((resolve, reject) => {
        const transaction = this.db!.transaction(storeName, 'readonly');
        const store = transaction.objectStore(storeName);
        const index = store.index(indexName);
        const request = index.getAll(value);
  
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
    }
  
    /**
     * Closes the database connection
     */
    public close(): void {
      if (this.db) {
        this.db.close();
        this.db = null;
      }
    }
  }
  
  // Export singleton instance
  export const indexedDB = IndexedDBService.getInstance();
  
  // Types for trading history
  export interface TradingHistoryItem {
    id: string;
    timestamp: number;
    symbol: string;
    type: 'buy' | 'sell';
    price: number;
    amount: number;
    total: number;
  }
  
  // Types for market data
  export interface MarketDataItem {
    id: string;
    symbol: string;
    timestamp: number;
    price: number;
    volume: number;
    high: number;
    low: number;
  }
  
  // Example usage:
  // await indexedDB.add('tradingHistory', { id: '1', timestamp: Date.now(), ... });
  // const history = await indexedDB.getAll<TradingHistoryItem>('tradingHistory');