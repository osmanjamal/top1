export const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };
  
  // التحقق من قوة كلمة المرور
  export const isStrongPassword = (password: string): {
    isValid: boolean;
    errors: string[];
  } => {
    const errors: string[] = [];
    
    if (password.length < 8) {
      errors.push('يجب أن تكون كلمة المرور 8 أحرف على الأقل');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('يجب أن تحتوي على حرف كبير واحد على الأقل');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('يجب أن تحتوي على حرف صغير واحد على الأقل');
    }
    if (!/[0-9]/.test(password)) {
      errors.push('يجب أن تحتوي على رقم واحد على الأقل');
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('يجب أن تحتوي على رمز خاص واحد على الأقل');
    }
  
    return {
      isValid: errors.length === 0,
      errors
    };
  };
  
  // التحقق من صحة رقم الهاتف
  export const isValidPhone = (phone: string): boolean => {
    const phoneRegex = /^((\+|00)966|0)?5[0-9]{8}$/;
    return phoneRegex.test(phone);
  };
  
  // التحقق من صحة الرقم المالي
  export const isValidAmount = (amount: string): boolean => {
    const amountRegex = /^\d+(\.\d{1,2})?$/;
    return amountRegex.test(amount);
  };
  
  // التحقق من API Key
  export const isValidApiKey = (apiKey: string): boolean => {
    // التحقق من طول المفتاح وتركيبته
    return /^[A-Za-z0-9-_]{32,64}$/.test(apiKey);
  };
  
  // التحقق من صحة اسم المستخدم
  export const isValidUsername = (username: string): boolean => {
    return /^[a-zA-Z0-9_-]{3,16}$/.test(username);
  };
  
  