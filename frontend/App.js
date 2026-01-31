import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { apiService } from './src/services/api';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  // 백엔드 API 호출 함수
  const handleApiCall = async () => {
    setLoading(true);
    setResponse(null);

    try {
      // 테스트 엔드포인트 호출
      const testResult = await apiService.test();
      Alert.alert('성공', `백엔드 연결 성공!\n${JSON.stringify(testResult, null, 2)}`);
      setResponse(testResult);
    } catch (error) {
      Alert.alert('오류', `API 호출 실패: ${error.message}`);
      console.error('API Error:', error);
    } finally {
      setLoading(false);
    }
  };

  // AI 채팅 API 호출 함수
  const handleAICall = async () => {
    setLoading(true);
    setResponse(null);

    try {
      const aiResult = await apiService.chatWithAI('안녕하세요! 테스트입니다.');
      Alert.alert('AI 응답', `응답: ${aiResult.response}\n모델: ${aiResult.model}`);
      setResponse(aiResult);
    } catch (error) {
      Alert.alert('오류', `AI API 호출 실패: ${error.message}`);
      console.error('AI API Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      <Text style={styles.title}>FastAPI + React Native</Text>
      <Text style={styles.subtitle}>해커톤 프로젝트</Text>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={handleApiCall}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#000" />
          ) : (
            <Text style={styles.buttonText}>백엔드 테스트</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.buttonSecondary, loading && styles.buttonDisabled]}
          onPress={handleAICall}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#000" />
          ) : (
            <Text style={styles.buttonText}>AI API 호출</Text>
          )}
        </TouchableOpacity>
      </View>

      {response && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseTitle}>응답:</Text>
          <Text style={styles.responseText}>
            {JSON.stringify(response, null, 2)}
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#76B900',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 40,
  },
  buttonContainer: {
    width: '100%',
    gap: 16,
  },
  button: {
    backgroundColor: '#76B900',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 50,
  },
  buttonSecondary: {
    backgroundColor: '#333',
    borderWidth: 1,
    borderColor: '#76B900',
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: '600',
  },
  responseContainer: {
    marginTop: 30,
    padding: 16,
    backgroundColor: '#1a1a1a',
    borderRadius: 8,
    width: '100%',
    maxHeight: 300,
  },
  responseTitle: {
    color: '#76B900',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  responseText: {
    color: '#fff',
    fontSize: 12,
    fontFamily: 'monospace',
  },
});

