import { format, formatDistance, parseISO } from 'date-fns';
import { ar } from 'date-fns/locale';

// تنسيق الأرقام والعملات
export const formatNumber = (value: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('ar-SA', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);
};

export const formatCurrency = (value: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

export const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('ar-SA', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value / 100);
};

// تنسيق التواريخ
export const formatDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, 'dd/MM/yyyy', { locale: ar });
};

export const formatDateTime = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, 'dd/MM/yyyy HH:mm:ss', { locale: ar });
};

export const formatTimeAgo = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistance(dateObj, new Date(), { 
    addSuffix: true,
    locale: ar 
  });
};

// تنسيق حجم الملفات
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 بايت';

  const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت', 'تيرابايت'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${parseFloat((bytes / Math.pow(1024, i)).toFixed(2))} ${sizes[i]}`;
};

// تنسيق الأرقام الكبيرة
export const formatLargeNumber = (value: number): string => {
  if (value < 1000) return value.toString();
  
  const suffixes = ['', 'ألف', 'مليون', 'مليار', 'تريليون'];
  const suffixIndex = Math.floor(Math.log10(value) / 3);
  const shortValue = value / Math.pow(1000, suffixIndex);
  
  return `${formatNumber(shortValue, 1)} ${suffixes[suffixIndex]}`;
};