export const generateId = (prefix: string = ''): string => {
    return `${prefix}${Math.random().toString(36).substr(2, 9)}_${Date.now()}`;
  };
  
  // تأخير تنفيذ العمليات
  export const delay = (ms: number): Promise<void> => {
    return new Promise(resolve => setTimeout(resolve, ms));
  };
  
  // تحويل كائن إلى سلسلة استعلام URL
  export const objectToQueryString = (obj: Record<string, any>): string => {
    return Object.entries(obj)
      .filter(([_, value]) => value !== undefined && value !== null)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
      .join('&');
  };
  
  // تقصير النص الطويل
  export const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };
  
  // تنسيق الرسالة حسب العدد
  export const pluralize = (count: number, singular: string, plural: string): string => {
    return count === 1 ? singular : plural;
  };
  
  // حفظ البيانات في التخزين المحلي
  export const storage = {
    set: (key: string, value: any): void => {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch (error) {
        console.error('Error saving to localStorage:', error);
      }
    },
    
    get: <T>(key: string, defaultValue: T): T => {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch (error) {
        console.error('Error reading from localStorage:', error);
        return defaultValue;
      }
    },
    
    remove: (key: string): void => {
      try {
        localStorage.removeItem(key);
      } catch (error) {
        console.error('Error removing from localStorage:', error);
      }
    },
    
    clear: (): void => {
      try {
        localStorage.clear();
      } catch (error) {
        console.error('Error clearing localStorage:', error);
      }
    }
  };
  
  // مساعد للتعامل مع الأخطاء
  export const handleError = (error: any): string => {
    if (error.response) {
      // خطأ من الخادم مع استجابة
      return error.response.data?.message || 'حدث خطأ في الخادم';
    } else if (error.request) {
      // خطأ في الاتصال
      return 'لا يمكن الاتصال بالخادم';
    } else {
      // خطأ آخر
      return error.message || 'حدث خطأ غير معروف';
    }
  };
  
  // دمج المصفوفات مع إزالة التكرار
  export const uniqueArray = <T>(arr: T[]): T[] => {
    return [...new Set(arr)];
  };
  
  // تنظيم المصفوفة
  export const sortArray = <T>(
    arr: T[],
    key: keyof T,
    order: 'asc' | 'desc' = 'asc'
  ): T[] => {
    return [...arr].sort((a, b) => {
      if (order === 'asc') {
        return a[key] > b[key] ? 1 : -1;
      }
      return a[key] < b[key] ? 1 : -1;
    });
  };
  
  // تجميع عناصر المصفوفة
  export const groupBy = <T>(
    arr: T[],
    key: keyof T
  ): Record<string, T[]> => {
    return arr.reduce((groups, item) => {
      const value = String(item[key]);
      groups[value] = groups[value] || [];
      groups[value].push(item);
      return groups;
    }, {} as Record<string, T[]>);
  };
  