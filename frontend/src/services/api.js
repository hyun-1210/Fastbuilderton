/**
 * 백엔드 API 통신 서비스
 * Android 에뮬레이터와 iOS 시뮬레이터를 자동으로 감지하여 적절한 베이스 URL 사용
 */
import axios from 'axios';
import { Platform } from 'react-native';

// 플랫폼별 베이스 URL 설정
const getBaseURL = () => {
  if (Platform.OS === 'android') {
    // Android 에뮬레이터는 10.0.2.2를 사용하여 호스트 머신의 localhost에 접근
    return 'http://10.0.2.2:8000';
  } else if (Platform.OS === 'ios') {
    // iOS 시뮬레이터는 localhost 사용 가능
    return 'http://127.0.0.1:8000';
  } else {
    // 웹 또는 기타 플랫폼
    return 'http://localhost:8000';
  }
};

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000, // 10초 타임아웃
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (로깅용)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (에러 처리)
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', error);
    if (error.response) {
      // 서버가 응답했지만 에러 상태 코드
      throw new Error(
        error.response.data?.detail || 
        `서버 오류: ${error.response.status}`
      );
    } else if (error.request) {
      // 요청은 보냈지만 응답을 받지 못함 (네트워크 오류)
      throw new Error(
        '백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.'
      );
    } else {
      // 요청 설정 중 오류 발생
      throw new Error(`요청 설정 오류: ${error.message}`);
    }
  }
);

/**
 * API 서비스 객체
 */
export const apiService = {
  /**
   * 백엔드 헬스 체크
   */
  async healthCheck() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  /**
   * 테스트 엔드포인트 호출
   */
  async test() {
    const response = await apiClient.get('/api/ai/test');
    return response.data;
  },

  /**
   * AI 채팅 API 호출
   * @param {string} prompt - 사용자 입력 프롬프트
   * @param {number} maxTokens - 최대 토큰 수 (기본값: 100)
   */
  async chatWithAI(prompt, maxTokens = 100) {
    const response = await apiClient.post('/api/ai/chat', {
      prompt,
      max_tokens: maxTokens,
    });
    return response.data;
  },
};

// 기본 내보내기 (선택사항)
export default apiService;

