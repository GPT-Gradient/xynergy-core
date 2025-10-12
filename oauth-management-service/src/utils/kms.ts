/**
 * KMS Encryption Service
 * Handles token encryption/decryption using GCP Cloud KMS
 */

import { KeyManagementServiceClient } from '@google-cloud/kms';
import { logger } from './logger';

const PROJECT_ID = process.env.PROJECT_ID || 'xynergy-dev-1757909467';
const LOCATION = process.env.KMS_LOCATION || 'us-central1';
const KEY_RING = process.env.KMS_KEY_RING || 'xynergy-oauth-keys';
const KEY_NAME = process.env.KMS_KEY_NAME || 'oauth-token-key';

class KMSService {
  private client: KeyManagementServiceClient;
  private keyPath: string;

  constructor() {
    this.client = new KeyManagementServiceClient();
    this.keyPath = this.client.cryptoKeyPath(PROJECT_ID, LOCATION, KEY_RING, KEY_NAME);
  }

  /**
   * Encrypt a token using GCP KMS
   */
  async encryptToken(plaintext: string): Promise<string> {
    try {
      const plaintextBuffer = Buffer.from(plaintext, 'utf8');

      const [encryptResponse] = await this.client.encrypt({
        name: this.keyPath,
        plaintext: plaintextBuffer,
      });

      if (!encryptResponse.ciphertext) {
        throw new Error('Encryption failed: no ciphertext returned');
      }

      // Return base64-encoded ciphertext
      const ciphertext = Buffer.from(encryptResponse.ciphertext).toString('base64');

      logger.debug('Token encrypted successfully', {
        plaintextLength: plaintext.length,
        ciphertextLength: ciphertext.length,
      });

      return ciphertext;
    } catch (error) {
      logger.error('Error encrypting token', { error });
      throw new Error('Failed to encrypt token');
    }
  }

  /**
   * Decrypt a token using GCP KMS
   */
  async decryptToken(ciphertext: string): Promise<string> {
    try {
      const ciphertextBuffer = Buffer.from(ciphertext, 'base64');

      const [decryptResponse] = await this.client.decrypt({
        name: this.keyPath,
        ciphertext: ciphertextBuffer,
      });

      if (!decryptResponse.plaintext) {
        throw new Error('Decryption failed: no plaintext returned');
      }

      const plaintext = Buffer.from(decryptResponse.plaintext).toString('utf8');

      logger.debug('Token decrypted successfully', {
        ciphertextLength: ciphertext.length,
        plaintextLength: plaintext.length,
      });

      return plaintext;
    } catch (error) {
      logger.error('Error decrypting token', { error });
      throw new Error('Failed to decrypt token');
    }
  }

  /**
   * Ensure KMS key ring and key exist
   */
  async ensureKeyExists(): Promise<void> {
    try {
      const keyRingPath = this.client.keyRingPath(PROJECT_ID, LOCATION, KEY_RING);

      // Try to get key ring
      try {
        await this.client.getKeyRing({ name: keyRingPath });
        logger.info('KMS key ring exists', { keyRing: KEY_RING });
      } catch (error: any) {
        if (error.code === 5) { // NOT_FOUND
          logger.info('Creating KMS key ring', { keyRing: KEY_RING });
          const locationPath = this.client.locationPath(PROJECT_ID, LOCATION);
          await this.client.createKeyRing({
            parent: locationPath,
            keyRingId: KEY_RING,
          });
        } else {
          throw error;
        }
      }

      // Try to get crypto key
      try {
        await this.client.getCryptoKey({ name: this.keyPath });
        logger.info('KMS crypto key exists', { key: KEY_NAME });
      } catch (error: any) {
        if (error.code === 5) { // NOT_FOUND
          logger.info('Creating KMS crypto key', { key: KEY_NAME });
          await this.client.createCryptoKey({
            parent: keyRingPath,
            cryptoKeyId: KEY_NAME,
            cryptoKey: {
              purpose: 'ENCRYPT_DECRYPT',
              versionTemplate: {
                algorithm: 'GOOGLE_SYMMETRIC_ENCRYPTION',
              },
            },
          });
        } else {
          throw error;
        }
      }

      logger.info('KMS setup verified', {
        project: PROJECT_ID,
        location: LOCATION,
        keyRing: KEY_RING,
        key: KEY_NAME,
      });
    } catch (error) {
      logger.error('Error ensuring KMS key exists', { error });
      throw error;
    }
  }

  /**
   * Test encryption/decryption
   */
  async testEncryption(): Promise<boolean> {
    try {
      const testData = 'test-token-' + Date.now();
      const encrypted = await this.encryptToken(testData);
      const decrypted = await this.decryptToken(encrypted);

      if (testData !== decrypted) {
        throw new Error('Encryption test failed: decrypted data does not match original');
      }

      logger.info('KMS encryption test passed');
      return true;
    } catch (error) {
      logger.error('KMS encryption test failed', { error });
      return false;
    }
  }
}

export const kmsService = new KMSService();
