import CryptoJS from 'crypto-js';

export interface EncryptedData {
  ciphertext: string;
  iv: string;
  salt: string;
}

export const encryptGeminiKey = (apiKey: string, secret: string): string => {
  // We'll use a standard format that we can parse in Python
  // For simplicity in this RAG project, we'll use a string format:
  // "salt:iv:ciphertext"
  
  const salt = CryptoJS.lib.WordArray.random(128 / 8);
  const iv = CryptoJS.lib.WordArray.random(128 / 8);
  
  const key = CryptoJS.PBKDF2(secret, salt, {
    keySize: 256 / 32,
    iterations: 1000
  });
  
  const encrypted = CryptoJS.AES.encrypt(apiKey, key, {
    iv: iv,
    padding: CryptoJS.pad.Pkcs7,
    mode: CryptoJS.mode.CBC
  });
  
  return `${salt.toString()}:${iv.toString()}:${encrypted.toString()}`;
};
