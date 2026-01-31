import React, { useState, useEffect, useRef } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Animated,
  Modal,
  Pressable,
  TextInput,
  ScrollView,
  Dimensions,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import Svg, { Polygon, Line, Circle, Defs, LinearGradient, Stop, G } from 'react-native-svg';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Android emulator can't use localhost — it points to the emulator. Use 10.0.2.2 to reach your computer.
// Physical device (any OS): use your computer's IP, e.g. 'http://192.168.1.5:8000'
const API_BASE = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
const AUTH_TOKEN_KEY = '@anbu_auth_token';
const USER_KEY = '@anbu_user';
const RADAR_COLORS = ['#9B7BCC', '#5BA8C9', '#5BA89A', '#C97B9A', '#C9A86B', '#8B7BAB', '#7BA8B9', '#7BA89A', '#B97B8A', '#B9A87B'];

// Temporary fake insights (will be replaced by DB later)
const INSIGHTS_DATA = [
  '관계 활동 전보다 24% 증가했어요.',
  '지난주 대비 연결 24% 늘었어요.',
  '관계 인사이트: 24% 성장 중.',
];

// Notifications (relationship alerts) – will be replaced by DB
const NOTIFICATIONS_DATA = [
  { id: '1', text: '엄마에게 전화한 지 10일이 지났어요.', icon: 'phone-outline', fullText: '엄마에게 전화한 지 10일이 지났어요. 가끔 연락하면 좋겠죠.' },
  { id: '2', text: '선배님 메시지에 5시간째 답장하지 않으셨아요.', icon: 'message-text-outline', fullText: '선배님 메시지에 5시간째 답장하지 않으셨아요. 빨리 답장해 보세요.' },
  { id: '3', text: '여자친구 생일이 15일 남았어요.', icon: 'heart-outline', fullText: '여자친구 생일이 15일 남았어요. 미리 준비해 두세요.' },
  { id: '4', text: '아빠와 2주 만에 연락해 보는 건 어때요?', icon: 'heart-outline', fullText: '아빠와 2주 만에 연락해 보는 건 어때요? 전화 한 통화 어떠세요?' },
  { id: '5', text: '동기 지민님이 3일 전 메시지를 보냈어요.', icon: 'message-text-outline', fullText: '동기 지민님이 3일 전 메시지를 보냈어요. 확인해 보세요.' },
  { id: '6', text: '할머니 생신이 일주일 남았어요.', icon: 'heart-outline', fullText: '할머니 생신이 일주일 남았어요. 미리 준비해 두세요.' },
];

// TODO: Replace with DB-backed relationship satisfaction scores. Shape/count may vary by user.
// Vibrant liquid palette – still refined, with a bit more pop.
const RELATIONSHIP_RADAR_DATA = [
  { label: '가족', score: 74, color: '#9B7BCC' },
  { label: '직장', score: 58, color: '#5BA8C9' },
  { label: '친구', score: 61, color: '#5BA89A' },
  { label: '연인', score: 42, color: '#C97B9A' },
  { label: '멘토', score: 55, color: '#C9A86B' },
];
// Overall average (63) – must be computed from DB or same source as above.
const OVERALL_SATISFACTION_SCORE = 63;

const NAV_ITEMS = [
  { key: 'home', label: '홈', icon: 'home-circle-outline', iconFilled: 'home-circle' },
  { key: 'relations', label: '관계', icon: 'heart-circle-outline', iconFilled: 'heart-circle' },
  { key: 'profile', label: '프로필', icon: 'account-circle-outline', iconFilled: 'account-circle' },
];

function NotificationsSection({ onOpenNotification }) {
  return (
    <View style={styles.notificationsSection}>
      <Text style={styles.notificationsTitle}>알림</Text>
      <View style={styles.notificationList}>
        {NOTIFICATIONS_DATA.map((item, index) => (
          <TouchableOpacity
            key={item.id}
            style={[
              styles.notificationRow,
              index === NOTIFICATIONS_DATA.length - 1 && styles.notificationRowLast,
            ]}
            onPress={() => onOpenNotification(item)}
            activeOpacity={0.6}
          >
            <MaterialCommunityIcons
              name={item.icon}
              size={20}
              color="#8E8E93"
              style={styles.notificationIcon}
            />
            <Text style={styles.notificationText} numberOfLines={1} ellipsizeMode="tail">
              {item.text}
            </Text>
            <MaterialCommunityIcons name="chevron-right" size={20} color="#C6C6C8" />
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

function SatisfactionCard({ overallScore = OVERALL_SATISFACTION_SCORE }) {
  const [index, setIndex] = useState(0);
  const fadeAnim = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    const interval = setInterval(() => {
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 280,
        useNativeDriver: true,
      }).start(() => {
        setIndex((i) => (i + 1) % INSIGHTS_DATA.length);
        Animated.timing(fadeAnim, {
          toValue: 1,
          duration: 320,
          useNativeDriver: true,
        }).start();
      });
    }, 8000);
    return () => clearInterval(interval);
  }, [fadeAnim]);

  return (
    <View style={styles.satisfactionCard}>
      <Animated.Text
        style={[styles.satisfactionTagline, { opacity: fadeAnim }]}
        numberOfLines={2}
      >
        {INSIGHTS_DATA[index]}
      </Animated.Text>
      <View style={styles.satisfactionRow}>
        <View>
          <Text style={styles.satisfactionLabel}>관계 만족도</Text>
          <Text style={styles.satisfactionSub}>전체 평균</Text>
        </View>
        <View style={styles.satisfactionScoreWrap}>
          <Text style={styles.satisfactionScore}>{Math.round(overallScore)}</Text>
          <Text style={styles.satisfactionScoreUnit}>점</Text>
        </View>
      </View>
    </View>
  );
}

const CHART_SIZE = 240;
const CHART_CX = CHART_SIZE / 2;
const CHART_CY = CHART_SIZE / 2;
const CHART_R = (CHART_SIZE / 2) * 0.72;
const AXIS_EXTENT = 1.22;
const LABEL_RADIUS = CHART_R * AXIS_EXTENT * 1.12;

function getPolygonVertex(cx, cy, r, index, n) {
  const angleDeg = 90 - index * (360 / n);
  const angle = angleDeg * (Math.PI / 180);
  return { x: cx + r * Math.cos(angle), y: cy - r * Math.sin(angle) };
}

function RelationshipRadarChart({ data: dataProp }) {
  const data = dataProp && dataProp.length > 0 ? dataProp : RELATIONSHIP_RADAR_DATA;
  const n = data.length;
  const axisEndPoints = [];
  const dataPoints = [];
  for (let i = 0; i < n; i++) {
    const axisEnd = getPolygonVertex(CHART_CX, CHART_CY, CHART_R * AXIS_EXTENT, i, n);
    axisEndPoints.push(axisEnd);
    const r = (data[i].score / 100) * CHART_R;
    const p = getPolygonVertex(CHART_CX, CHART_CY, r, i, n);
    dataPoints.push({ ...p, color: data[i].color });
  }
  const dataPolygonPoints = dataPoints.map((d) => `${d.x},${d.y}`).join(' ');
  const gridLevels = [0.25, 0.5, 0.75, 1];

  return (
    <View style={[styles.radarChartWrap, { width: CHART_SIZE, height: CHART_SIZE }]}>
      <Svg width={CHART_SIZE} height={CHART_SIZE} style={styles.radarSvg}>
        <Defs>
          <LinearGradient id="radarFill" x1="0%" y1="0%" x2="100%" y2="100%">
            <Stop offset="0%" stopColor="#9B6BEB" stopOpacity="0.48" />
            <Stop offset="35%" stopColor="#7C4DFF" stopOpacity="0.48" />
            <Stop offset="65%" stopColor="#A88BEB" stopOpacity="0.48" />
            <Stop offset="100%" stopColor="#7C4DFF" stopOpacity="0.48" />
          </LinearGradient>
        </Defs>
        {gridLevels.map((level) => {
          const pts = [];
          for (let i = 0; i < n; i++) {
            const p = getPolygonVertex(CHART_CX, CHART_CY, CHART_R * level, i, n);
            pts.push(`${p.x},${p.y}`);
          }
          return (
            <Polygon
              key={level}
              points={pts.join(' ')}
              fill="none"
              stroke="rgba(124, 77, 255, 0.18)"
              strokeWidth={1.2}
            />
          );
        })}
        {axisEndPoints.map((v, i) => (
          <Line
            key={`axis-${i}`}
            x1={CHART_CX}
            y1={CHART_CY}
            x2={v.x}
            y2={v.y}
            stroke="rgba(124, 77, 255, 0.18)"
            strokeWidth={1.2}
          />
        ))}
        <Polygon
          points={dataPolygonPoints}
          fill="url(#radarFill)"
          stroke="rgba(124, 77, 255, 0.28)"
          strokeWidth={2.5}
        />
        {dataPoints.map((d, i) => (
          <G key={i}>
            <Circle
              cx={d.x}
              cy={d.y}
              r={10}
              fill={d.color}
              fillOpacity={0.28}
            />
            <Circle
              cx={d.x}
              cy={d.y}
              r={6}
              fill={d.color}
              stroke="rgba(255,255,255,0.95)"
              strokeWidth={2}
            />
          </G>
        ))}
      </Svg>
      <View style={[styles.radarLabels, { width: CHART_SIZE, height: CHART_SIZE }]} pointerEvents="box-none">
        {data.map((item, i) => {
          const v = getPolygonVertex(CHART_CX, CHART_CY, LABEL_RADIUS, i, n);
          const isLeft = v.x < CHART_CX;
          const leftOffset = isLeft ? 6 : 0;
          const topOffset = i === 0 ? 6 : 0;
          return (
            <View
              key={item.label}
              style={[
                styles.radarLabelItem,
                {
                  position: 'absolute',
                  left: v.x - 26 - leftOffset,
                  top: v.y - 12 - topOffset,
                  width: 52,
                  alignItems: isLeft ? 'flex-end' : 'center',
                },
              ]}
            >
              <Text style={styles.radarLabelText} numberOfLines={1}>
                {item.label}
              </Text>
              <Text style={[styles.radarLabelScore, { color: item.color }]}>{item.score}%</Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const COLLAPSED_NOTIF_COUNT = 2;
const EXPANDED_NOTIF_COUNT = 4;

function FloatingInboxBubble({
  value,
  onChangeText,
  onSend,
  onOpenNotification,
  onSeeAllNotifications,
}) {
  const [expanded, setExpanded] = useState(false);
  const displayNotifications = NOTIFICATIONS_DATA.slice(
    0,
    expanded ? EXPANDED_NOTIF_COUNT : COLLAPSED_NOTIF_COUNT
  );

  return (
    <View style={styles.floatingInboxRoot}>
      <View style={styles.floatingSuggestions}>
        <TouchableOpacity
          style={styles.floatingBubbleExpand}
          onPress={() => setExpanded(!expanded)}
          activeOpacity={0.7}
        >
          <MaterialCommunityIcons
            name={expanded ? 'chevron-down' : 'chevron-up'}
            size={18}
            color="rgba(0, 0, 0, 0.4)"
          />
        </TouchableOpacity>
        {displayNotifications.map((item, index) => (
          <TouchableOpacity
            key={item.id}
            style={styles.floatingBubbleNotifRow}
            onPress={() => onOpenNotification(item)}
            activeOpacity={0.6}
          >
            <MaterialCommunityIcons
              name={item.icon}
              size={16}
              color="rgba(0, 0, 0, 0.45)"
              style={styles.floatingBubbleNotifIcon}
            />
            <Text style={styles.floatingBubbleNotifText} numberOfLines={1} ellipsizeMode="tail">
              {item.text}
            </Text>
          </TouchableOpacity>
        ))}
        {expanded && (
          <TouchableOpacity
            style={styles.floatingBubbleSeeAll}
            onPress={onSeeAllNotifications}
            activeOpacity={0.7}
          >
            <Text style={styles.floatingBubbleSeeAllText}>알림 전체 보기</Text>
          </TouchableOpacity>
        )}
      </View>
      <View style={styles.chatBubble}>
        <TextInput
          style={styles.chatInput}
          placeholder="메시지를 입력하세요"
          placeholderTextColor="#8E8E93"
          value={value}
          onChangeText={onChangeText}
          multiline={false}
          maxLength={500}
        />
        <TouchableOpacity
          style={styles.chatSendButton}
          onPress={onSend}
          activeOpacity={0.8}
        >
          <MaterialCommunityIcons name="send" size={22} color="#FFFFFF" />
        </TouchableOpacity>
      </View>
    </View>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [showAllInsights, setShowAllInsights] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [showAllNotifications, setShowAllNotifications] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [authToken, setAuthToken] = useState(null);
  const [user, setUser] = useState(null);
  const [radarData, setRadarData] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [relationsCategories, setRelationsCategories] = useState([]);
  const [relationsPersonas, setRelationsPersonas] = useState([]);
  const [relationsFilter, setRelationsFilter] = useState('all');
  const [relationsExpanded, setRelationsExpanded] = useState({});
  const [showAddCategoryModal, setShowAddCategoryModal] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [addingCategory, setAddingCategory] = useState(false);

  const radarChartData = radarData?.categories?.length
    ? radarData.categories.map((c, i) => ({
        label: c.name,
        score: Math.round(Number(c.score)),
        color: RADAR_COLORS[i % RADAR_COLORS.length],
      }))
    : null;
  const overallScore = radarData?.overall_score ?? OVERALL_SATISFACTION_SCORE;

  useEffect(() => {
    (async () => {
      try {
        const [token, userJson] = await Promise.all([
          AsyncStorage.getItem(AUTH_TOKEN_KEY),
          AsyncStorage.getItem(USER_KEY),
        ]);
        if (token) setAuthToken(token);
        if (userJson) {
          try {
            setUser(JSON.parse(userJson));
          } catch (_) {
            setUser({ email: '로그인된 계정' });
          }
        } else if (token) {
          setUser({ email: '로그인된 계정' });
        }
      } catch (e) {
        console.warn('Restore auth failed', e);
      } finally {
        setAuthLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (!authToken) {
      setRadarData(null);
      return;
    }
    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/users/me/radar`, {
          headers: { Authorization: `Bearer ${authToken}` },
        });
        if (res.ok) {
          const data = await res.json();
          setRadarData(data);
        } else {
          setRadarData(null);
        }
      } catch (e) {
        console.warn('Fetch radar failed', e);
        setRadarData(null);
      }
    })();
  }, [authToken]);

  useEffect(() => {
    if (!authToken) {
      setRelationsCategories([]);
      setRelationsPersonas([]);
      return;
    }
    (async () => {
      try {
        const [catRes, perRes] = await Promise.all([
          fetch(`${API_BASE}/api/categories`, { headers: { Authorization: `Bearer ${authToken}` } }),
          fetch(`${API_BASE}/api/personas`, { headers: { Authorization: `Bearer ${authToken}` } }),
        ]);
        if (catRes.ok) {
          const data = await catRes.json();
          setRelationsCategories(Array.isArray(data) ? data : []);
        }
        if (perRes.ok) {
          const data = await perRes.json();
          setRelationsPersonas(Array.isArray(data) ? data : []);
        }
      } catch (e) {
        console.warn('Fetch relations failed', e);
      }
    })();
  }, [authToken]);

  const relationsCategoriesWithPersonas = relationsCategories.map((cat) => {
    const personas = relationsPersonas.filter((p) => p.category_id === cat.id);
    const avg = personas.length ? personas.reduce((s, p) => s + Number(p.relationship_temp || 0), 0) / personas.length : 0;
    return { ...cat, personas, avg: Math.round(avg) };
  });
  const relationsTotalCount = relationsPersonas.length;
  const toggleCategoryExpanded = (id) => {
    setRelationsExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };
  const handleAddCategory = async () => {
    const name = newCategoryName.trim();
    if (!name || !authToken) return;
    setAddingCategory(true);
    try {
      const res = await fetch(`${API_BASE}/api/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authToken}` },
        body: JSON.stringify({ name }),
      });
      if (res.ok) {
        const created = await res.json();
        setRelationsCategories((prev) => [...prev, created]);
        setNewCategoryName('');
        setShowAddCategoryModal(false);
      }
    } catch (e) {
      console.warn('Add category failed', e);
    } finally {
      setAddingCategory(false);
    }
  };

  const handleLogin = async () => {
    const email = loginEmail.trim();
    const password = loginPassword.trim();
    setLoginError('');
    if (!email || !password) {
      setLoginError('이메일과 비밀번호를 입력하세요.');
      return;
    }
    setLoginLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      let data = {};
      try {
        data = await res.json();
      } catch (_) {
        setLoginError('서버 응답을 읽을 수 없습니다. 백엔드가 실행 중인지 확인하세요.');
        return;
      }
      if (!res.ok) {
        const msg = data.detail || '이메일 또는 비밀번호를 확인하세요.';
        setLoginError(Array.isArray(msg) ? msg.join(' ') : String(msg));
        return;
      }
      const token = data.access_token ?? data.accessToken ?? null;
      const rawUser = data.user;
      const userObj = rawUser && typeof rawUser === 'object'
        ? { email: rawUser.email ?? email, id: rawUser.id ?? '' }
        : { email, id: '' };
      if (!token) {
        setLoginError('서버에서 토큰을 받지 못했습니다.');
        return;
      }
      setAuthToken(token);
      setUser({ ...userObj, email: userObj.email || email });
      setLoginEmail('');
      setLoginPassword('');
      setLoginError('');
      AsyncStorage.setItem(AUTH_TOKEN_KEY, token).catch(() => {});
      AsyncStorage.setItem(USER_KEY, JSON.stringify(userObj)).catch(() => {});
      Alert.alert('로그인 성공', `${userObj.email || email}으로 로그인되었습니다.`);
    } catch (e) {
      const msg = e?.message || '서버에 연결할 수 없습니다.';
      setLoginError(`${msg} (API: ${API_BASE})`);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = async () => {
    setAuthToken(null);
    setUser(null);
    setRadarData(null);
    await AsyncStorage.multiRemove([AUTH_TOKEN_KEY, USER_KEY]);
  };

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      // TODO: send message
      setChatMessage('');
    }
  };

  const windowHeight = Dimensions.get('window').height;

  return (
    <View style={[styles.container, styles.containerFixed, { height: windowHeight }]}>
      <StatusBar style="dark" />
      <View style={styles.headerRow}>
        <Text style={styles.logo}>ANBU</Text>
      </View>
      <View style={styles.mainContent}>
        {activeTab === 'home' ? (
          <ScrollView
            style={styles.homeScroll}
            contentContainerStyle={styles.homeScrollContent}
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.mainContentCard}>
              <View style={styles.satisfactionCardWrap}>
                <SatisfactionCard overallScore={overallScore} />
              </View>
              <View style={styles.radarBackground} pointerEvents="none">
                <RelationshipRadarChart data={radarChartData} />
              </View>
            </View>
          </ScrollView>
        ) : activeTab === 'relations' ? (
          <ScrollView
            style={styles.relationsScroll}
            contentContainerStyle={styles.relationsScrollContent}
            showsVerticalScrollIndicator={false}
          >
            <View style={styles.relationsHeader}>
              <MaterialCommunityIcons name="account-group" size={40} color="#7C4DFF" />
              <View style={styles.relationsHeaderText}>
                <Text style={styles.relationsTitle}>내 사람들</Text>
                <Text style={styles.relationsSubtitle}>
                  {authToken ? `총 ${relationsTotalCount}명` : '로그인하면 내 사람들을 볼 수 있어요'}
                </Text>
              </View>
            </View>
            {authToken ? (
            <>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.relationsBubblesWrap}
              contentContainerStyle={styles.relationsBubblesContent}
            >
              <TouchableOpacity
                style={[styles.relationsBubble, relationsFilter === 'all' && styles.relationsBubbleActive]}
                onPress={() => setRelationsFilter('all')}
                activeOpacity={0.8}
              >
                <Text style={[styles.relationsBubbleText, relationsFilter === 'all' && styles.relationsBubbleTextActive]}>전체</Text>
              </TouchableOpacity>
              {relationsCategories.map((cat) => (
                <TouchableOpacity
                  key={cat.id}
                  style={[styles.relationsBubble, relationsFilter === cat.id && styles.relationsBubbleActive]}
                  onPress={() => setRelationsFilter(cat.id)}
                  activeOpacity={0.8}
                >
                  <Text style={[styles.relationsBubbleText, relationsFilter === cat.id && styles.relationsBubbleTextActive]}>{cat.name}</Text>
                </TouchableOpacity>
              ))}
              <TouchableOpacity
                style={styles.relationsBubbleAdd}
                onPress={() => setShowAddCategoryModal(true)}
                activeOpacity={0.8}
              >
                <MaterialCommunityIcons name="plus" size={24} color="#7C4DFF" />
              </TouchableOpacity>
            </ScrollView>
            <View style={styles.relationsSections}>
              {(relationsFilter === 'all' ? relationsCategoriesWithPersonas : relationsCategoriesWithPersonas.filter((c) => c.id === relationsFilter)).map((cat) => {
                const expanded = relationsExpanded[cat.id];
                const count = cat.personas.length;
                const pct = count ? cat.avg : 0;
                return (
                  <View key={cat.id} style={styles.relationsCategoryBlock}>
                    <TouchableOpacity
                      style={styles.relationsCategoryHeader}
                      onPress={() => toggleCategoryExpanded(cat.id)}
                      activeOpacity={0.7}
                    >
                      <MaterialCommunityIcons name="account-group" size={28} color="#7C4DFF" />
                      <View style={styles.relationsCategoryHeaderText}>
                        <Text style={styles.relationsCategoryName}>{cat.name}</Text>
                        <Text style={styles.relationsCategoryMeta}>{count}명 {pct}%</Text>
                      </View>
                      <MaterialCommunityIcons name={expanded ? 'chevron-up' : 'chevron-down'} size={24} color="#8E8E93" />
                    </TouchableOpacity>
                    {expanded ? (
                      <View style={styles.relationsPersonasList}>
                        {cat.personas.map((p) => (
                          <View key={p.id} style={styles.relationsPersonaCard}>
                            <View style={styles.relationsPersonaCardLeft}>
                              <View style={styles.relationsPersonaAvatar} />
                              <View>
                                <Text style={styles.relationsPersonaName}>{p.name}</Text>
                                <Text style={styles.relationsPersonaPct}>{Math.round(Number(p.relationship_temp || 0))}%</Text>
                              </View>
                            </View>
                            <MaterialCommunityIcons name="lightning-bolt" size={20} color="#7C4DFF" />
                          </View>
                        ))}
                      </View>
                    ) : null}
                  </View>
                );
              })}
            </View>
            </>
            ) : null}
          </ScrollView>
        ) : activeTab === 'profile' ? (
          <View style={[styles.profileTabWrap, { minHeight: windowHeight - 220 }]} pointerEvents="box-none">
            <ScrollView
              style={styles.profileScroll}
              contentContainerStyle={styles.profileScrollContent}
              keyboardShouldPersistTaps="handled"
              showsVerticalScrollIndicator={true}
            >
              <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : undefined}
                style={styles.profileInner}
                pointerEvents="box-none"
              >
                <Text style={styles.profileScreenTitle}>프로필</Text>
                {authLoading ? (
                  <View style={styles.profileLoading}>
                    <ActivityIndicator size="large" color="#7C4DFF" />
                  </View>
                ) : authToken && user ? (
                  <View style={styles.profileLoggedIn} pointerEvents="auto">
                    <MaterialCommunityIcons name="account-circle" size={64} color="#7C4DFF" />
                    <Text style={styles.profileEmail}>{user.email}</Text>
                    <Text style={styles.profileSub}>로그인된 계정</Text>
                    <TouchableOpacity
                      style={styles.profileLogoutBtn}
                      onPress={handleLogout}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.profileLogoutText}>로그아웃</Text>
                    </TouchableOpacity>
                  </View>
                ) : (
                  <View style={styles.profileForm} pointerEvents="auto">
                    <Text style={styles.profileTitle}>로그인</Text>
                    <Text style={styles.profileDemoHint}>
                      데모: demo@anbu.app / 비밀번호 anbu2025
                    </Text>
                    <TextInput
                      style={styles.profileInput}
                      placeholder="이메일"
                      placeholderTextColor="#8E8E93"
                      value={loginEmail}
                      onChangeText={(t) => { setLoginEmail(t); setLoginError(''); }}
                      autoCapitalize="none"
                      keyboardType="email-address"
                      editable={!loginLoading}
                      importantForAutofill="yes"
                    />
                    <TextInput
                      style={styles.profileInput}
                      placeholder="비밀번호"
                      placeholderTextColor="#8E8E93"
                      value={loginPassword}
                      onChangeText={(t) => { setLoginPassword(t); setLoginError(''); }}
                      secureTextEntry
                      editable={!loginLoading}
                      importantForAutofill="yes"
                    />
                    <TouchableOpacity
                      style={[styles.profileLoginBtn, loginLoading && styles.profileLoginBtnDisabled]}
                      onPress={handleLogin}
                      disabled={loginLoading}
                      activeOpacity={0.8}
                    >
                      {loginLoading ? (
                        <ActivityIndicator size="small" color="#FFFFFF" />
                      ) : (
                        <Text style={styles.profileLoginText}>로그인</Text>
                      )}
                    </TouchableOpacity>
                    {loginError ? (
                      <Text style={styles.profileLoginError}>{loginError}</Text>
                    ) : null}
                  </View>
                )}
              </KeyboardAvoidingView>
            </ScrollView>
          </View>
        ) : (
          <View style={styles.tabPlaceholder} />
        )}
      </View>

      {activeTab === 'home' && (
        <View style={styles.floatingBubbleWrap} pointerEvents="box-none">
          <FloatingInboxBubble
            value={chatMessage}
            onChangeText={setChatMessage}
            onSend={handleSendMessage}
            onOpenNotification={setSelectedNotification}
            onSeeAllNotifications={() => setShowAllNotifications(true)}
          />
        </View>
      )}

      <Modal
        visible={showAllInsights}
        transparent
        animationType="fade"
        onRequestClose={() => setShowAllInsights(false)}
      >
        <Pressable
          style={styles.modalBackdrop}
          onPress={() => setShowAllInsights(false)}
        >
          <Pressable style={styles.insightsModal} onPress={(e) => e.stopPropagation()}>
            <View style={styles.insightsModalHeader}>
              <Text style={styles.insightsModalTitle}>인사이트</Text>
              <TouchableOpacity
                onPress={() => setShowAllInsights(false)}
                style={styles.insightsModalClose}
                hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
              >
                <MaterialCommunityIcons name="close" size={24} color="#6B4EBB" />
              </TouchableOpacity>
            </View>
            {INSIGHTS_DATA.map((text, i) => (
              <View key={i} style={styles.insightItem}>
                <Text style={styles.insightItemText}>{text}</Text>
              </View>
            ))}
          </Pressable>
        </Pressable>
      </Modal>

      <Modal
        visible={!!selectedNotification}
        transparent
        animationType="fade"
        onRequestClose={() => setSelectedNotification(null)}
      >
        <Pressable
          style={styles.modalBackdrop}
          onPress={() => setSelectedNotification(null)}
        >
          <Pressable
            style={styles.notificationDetailModal}
            onPress={(e) => e.stopPropagation()}
          >
            {selectedNotification && (
              <>
                <View style={styles.notificationDetailHeader}>
                  <Text style={styles.notificationDetailTitle}>알림</Text>
                  <TouchableOpacity
                    onPress={() => setSelectedNotification(null)}
                    style={styles.insightsModalClose}
                    hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
                  >
                    <MaterialCommunityIcons name="close" size={22} color="#8E8E93" />
                  </TouchableOpacity>
                </View>
                <Text style={styles.notificationDetailText}>
                  {selectedNotification.fullText}
                </Text>
              </>
            )}
          </Pressable>
        </Pressable>
      </Modal>

      <Modal
        visible={showAllNotifications}
        transparent
        animationType="fade"
        onRequestClose={() => setShowAllNotifications(false)}
      >
        <Pressable
          style={styles.modalBackdrop}
          onPress={() => setShowAllNotifications(false)}
        >
          <Pressable
            style={styles.allNotificationsModal}
            onPress={(e) => e.stopPropagation()}
          >
            <View style={styles.notificationDetailHeader}>
              <Text style={styles.notificationDetailTitle}>알림</Text>
              <TouchableOpacity
                onPress={() => setShowAllNotifications(false)}
                style={styles.insightsModalClose}
                hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
              >
                <MaterialCommunityIcons name="close" size={22} color="#8E8E93" />
              </TouchableOpacity>
            </View>
            <View style={styles.allNotificationsList}>
              {NOTIFICATIONS_DATA.map((item, index) => (
                <TouchableOpacity
                  key={item.id}
                  style={[
                    styles.notificationRow,
                    index === NOTIFICATIONS_DATA.length - 1 && styles.notificationRowLast,
                  ]}
                  onPress={() => {
                    setShowAllNotifications(false);
                    setSelectedNotification(item);
                  }}
                  activeOpacity={0.6}
                >
                  <MaterialCommunityIcons
                    name={item.icon}
                    size={20}
                    color="#8E8E93"
                    style={styles.notificationIcon}
                  />
                  <Text style={styles.notificationText} numberOfLines={1} ellipsizeMode="tail">
                    {item.text}
                  </Text>
                  <MaterialCommunityIcons name="chevron-right" size={20} color="#C6C6C8" />
                </TouchableOpacity>
              ))}
            </View>
          </Pressable>
        </Pressable>
      </Modal>

      <Modal
        visible={showAddCategoryModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowAddCategoryModal(false)}
      >
        <Pressable style={styles.modalBackdrop} onPress={() => setShowAddCategoryModal(false)}>
          <Pressable style={styles.addCategoryModal} onPress={(e) => e.stopPropagation()}>
            <Text style={styles.addCategoryModalTitle}>새 카테고리</Text>
            <TextInput
              style={styles.profileInput}
              placeholder="카테고리 이름 (예: 가족, 직장)"
              placeholderTextColor="#8E8E93"
              value={newCategoryName}
              onChangeText={setNewCategoryName}
              editable={!addingCategory}
            />
            <View style={styles.addCategoryModalButtons}>
              <TouchableOpacity style={styles.addCategoryCancelBtn} onPress={() => setShowAddCategoryModal(false)} activeOpacity={0.8}>
                <Text style={styles.addCategoryCancelText}>취소</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.addCategoryOkBtn, addingCategory && styles.profileLoginBtnDisabled]}
                onPress={handleAddCategory}
                disabled={addingCategory || !newCategoryName.trim()}
                activeOpacity={0.8}
              >
                {addingCategory ? <ActivityIndicator size="small" color="#FFFFFF" /> : <Text style={styles.profileLoginText}>추가</Text>}
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
      </Modal>

      <View style={styles.navBar}>
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.key;
          return (
            <TouchableOpacity
              key={item.key}
              style={styles.navItem}
              onPress={() => setActiveTab(item.key)}
              activeOpacity={0.7}
            >
              <View style={[styles.iconWrap, isActive && styles.iconWrapActive]}>
                <MaterialCommunityIcons
                  name={isActive ? item.iconFilled : item.icon}
                  size={32}
                  color={isActive ? '#7C4DFF' : '#9E9EA6'}
                />
              </View>
              <Text style={[styles.navLabel, isActive && styles.navLabelActive]}>
                {item.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F0FA',
  },
  containerFixed: {
    overflow: 'hidden',
  },
  mainContent: {
    flex: 1,
    paddingTop: 4,
    paddingBottom: 200,
  },
  mainContentCard: {
    position: 'relative',
    minHeight: 420,
    marginHorizontal: 20,
    marginTop: 8,
    marginBottom: 200,
  },
  radarBackground: {
    position: 'absolute',
    top: 200,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },
  satisfactionCardWrap: {
    position: 'relative',
    zIndex: 2,
    paddingTop: 6,
    paddingHorizontal: 0,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 52,
    paddingBottom: 8,
    backgroundColor: 'transparent',
  },
  logo: {
    fontSize: 22,
    fontWeight: '700',
    color: '#7C4DFF',
    letterSpacing: 0.5,
  },
  satisfactionCard: {
    marginHorizontal: 4,
    marginTop: 0,
    marginBottom: 16,
    paddingVertical: 18,
    paddingHorizontal: 24,
    backgroundColor: 'rgba(255, 255, 255, 0.96)',
    borderRadius: 22,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: 'rgba(124, 77, 255, 0.1)',
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 12,
    elevation: 3,
  },
  satisfactionTagline: {
    fontSize: 16,
    fontWeight: '500',
    color: '#2C2C2E',
    marginBottom: 16,
    lineHeight: 24,
  },
  satisfactionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  satisfactionLabel: {
    fontSize: 13,
    fontWeight: '300',
    color: '#8E8E93',
    letterSpacing: 0.2,
  },
  satisfactionSub: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1C1C1E',
    marginTop: 2,
  },
  satisfactionScoreWrap: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  satisfactionScore: {
    fontSize: 32,
    fontWeight: '700',
    color: '#6B4EBB',
  },
  satisfactionScoreUnit: {
    fontSize: 16,
    fontWeight: '500',
    color: '#8E8E93',
    marginLeft: 4,
  },
  radarChartWrap: {
    width: CHART_SIZE,
    height: CHART_SIZE,
    alignSelf: 'center',
    opacity: 0.88,
  },
  radarSvg: {
    position: 'absolute',
    left: 0,
    top: 0,
  },
  radarLabels: {
    position: 'absolute',
    left: 0,
    top: 0,
    width: CHART_SIZE,
    height: CHART_SIZE,
  },
  radarLabelItem: {
    justifyContent: 'center',
  },
  radarLabelText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#2C2C2E',
  },
  radarLabelScore: {
    fontSize: 13,
    fontWeight: '700',
    marginTop: 4,
  },
  notificationsSection: {
    marginTop: 24,
    marginBottom: 12,
  },
  notificationsTitle: {
    fontSize: 13,
    fontWeight: '500',
    color: '#8E8E93',
    marginBottom: 8,
    marginHorizontal: 20,
    letterSpacing: -0.2,
  },
  notificationList: {
    backgroundColor: '#FFFFFF',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: '#E5E5EA',
  },
  notificationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: '#E5E5EA',
  },
  notificationRowLast: {
    borderBottomWidth: 0,
  },
  notificationIcon: {
    marginRight: 12,
  },
  notificationText: {
    flex: 1,
    fontSize: 15,
    fontWeight: '400',
    color: '#1C1C1E',
    lineHeight: 22,
  },
  notificationDetailModal: {
    width: '100%',
    maxWidth: 340,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 22,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#E8E8EC',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 8,
  },
  notificationDetailHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  notificationDetailTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  allNotificationsModal: {
    width: '100%',
    maxWidth: 360,
    maxHeight: '80%',
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 20,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#E8E8EC',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 8,
  },
  allNotificationsList: {
    marginTop: 8,
  },
  notificationDetailText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#3C3C43',
    lineHeight: 24,
  },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(107, 78, 187, 0.25)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  insightsModal: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    borderRadius: 28,
    padding: 24,
    borderWidth: 1,
    borderColor: 'rgba(124, 77, 255, 0.15)',
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.2,
    shadowRadius: 32,
    elevation: 12,
  },
  insightsModalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  insightsModalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#7C4DFF',
  },
  insightsModalClose: {
    padding: 4,
  },
  insightItem: {
    paddingVertical: 16,
    paddingHorizontal: 18,
    marginBottom: 10,
    backgroundColor: 'rgba(124, 77, 255, 0.1)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(124, 77, 255, 0.18)',
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 8,
    elevation: 2,
  },
  insightItemText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#6B4EBB',
    lineHeight: 22,
  },
  homeScroll: {
    flex: 1,
  },
  homeScrollContent: {
    paddingBottom: 24,
    paddingHorizontal: 0,
  },
  tabPlaceholder: {
    flex: 1,
  },
  relationsScroll: {
    flex: 1,
  },
  relationsScrollContent: {
    paddingBottom: 24,
    paddingHorizontal: 16,
  },
  relationsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  relationsHeaderText: {
    marginLeft: 12,
  },
  relationsTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#1C1C1E',
  },
  relationsSubtitle: {
    fontSize: 15,
    color: '#8E8E93',
    marginTop: 2,
  },
  relationsBubblesWrap: {
    marginBottom: 20,
  },
  relationsBubblesContent: {
    paddingRight: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  relationsBubble: {
    paddingVertical: 10,
    paddingHorizontal: 18,
    borderRadius: 20,
    backgroundColor: '#E5E5EA',
    marginRight: 10,
  },
  relationsBubbleActive: {
    backgroundColor: '#7C4DFF',
  },
  relationsBubbleText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  relationsBubbleTextActive: {
    color: '#FFFFFF',
  },
  relationsBubbleAdd: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(124, 77, 255, 0.15)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  relationsSections: {
    gap: 0,
  },
  relationsCategoryBlock: {
    marginBottom: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#E5E5EA',
  },
  relationsCategoryHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 14,
    paddingHorizontal: 16,
  },
  relationsCategoryHeaderText: {
    flex: 1,
    marginLeft: 12,
  },
  relationsCategoryName: {
    fontSize: 17,
    fontWeight: '700',
    color: '#1C1C1E',
  },
  relationsCategoryMeta: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 2,
  },
  relationsPersonasList: {
    paddingHorizontal: 16,
    paddingBottom: 16,
    gap: 8,
  },
  relationsPersonaCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F5F5F7',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 14,
    marginTop: 8,
  },
  relationsPersonaCardLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  relationsPersonaAvatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(124, 77, 255, 0.2)',
    marginRight: 12,
  },
  relationsPersonaName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1C1C1E',
  },
  relationsPersonaPct: {
    fontSize: 14,
    fontWeight: '700',
    color: '#7C4DFF',
    marginTop: 2,
  },
  addCategoryModal: {
    width: '100%',
    maxWidth: 340,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: '#E8E8EC',
  },
  addCategoryModalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1C1C1E',
    marginBottom: 20,
  },
  addCategoryModalButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: 12,
    marginTop: 16,
  },
  addCategoryCancelBtn: {
    paddingVertical: 12,
    paddingHorizontal: 20,
  },
  addCategoryCancelText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#8E8E93',
  },
  addCategoryOkBtn: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    backgroundColor: '#7C4DFF',
    borderRadius: 12,
    minWidth: 80,
    alignItems: 'center',
  },
  profileTabWrap: {
    flex: 1,
    width: '100%',
  },
  profileScreenTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1C1C1E',
    marginBottom: 20,
  },
  profileScroll: {
    flex: 1,
    width: '100%',
  },
  profileScrollContent: {
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingTop: 16,
    paddingBottom: 48,
  },
  profileInner: {
    flex: 1,
    minHeight: 280,
  },
  profileLoading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: 200,
  },
  profileLoggedIn: {
    alignItems: 'center',
  },
  profileEmail: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1C1C1E',
    marginTop: 12,
  },
  profileSub: {
    fontSize: 14,
    color: '#8E8E93',
    marginTop: 4,
  },
  profileLogoutBtn: {
    marginTop: 24,
    paddingVertical: 12,
    paddingHorizontal: 24,
    backgroundColor: 'rgba(124, 77, 255, 0.15)',
    borderRadius: 12,
  },
  profileLogoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#7C4DFF',
  },
  profileForm: {
    minHeight: 260,
  },
  profileTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#1C1C1E',
    marginBottom: 8,
  },
  profileDemoHint: {
    fontSize: 13,
    color: '#8E8E93',
    marginBottom: 20,
  },
  profileInput: {
    height: 48,
    borderWidth: 1,
    borderColor: '#E5E5EA',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#1C1C1E',
    backgroundColor: '#FFFFFF',
    marginBottom: 12,
  },
  profileLoginBtn: {
    height: 48,
    borderRadius: 12,
    backgroundColor: '#7C4DFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
  },
  profileLoginBtnDisabled: {
    opacity: 0.7,
  },
  profileLoginText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  profileLoginError: {
    fontSize: 13,
    color: '#C62828',
    marginTop: 12,
    textAlign: 'center',
  },
  floatingBubbleWrap: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 124,
    zIndex: 10,
  },
  floatingInboxRoot: {
    alignItems: 'stretch',
  },
  floatingSuggestions: {
    backgroundColor: 'transparent',
    marginBottom: 8,
  },
  floatingBubbleExpand: {
    alignItems: 'center',
    paddingVertical: 4,
    paddingTop: 4,
  },
  floatingBubbleNotifRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    paddingHorizontal: 4,
    backgroundColor: 'transparent',
  },
  floatingBubbleNotifIcon: {
    marginRight: 10,
  },
  floatingBubbleNotifText: {
    flex: 1,
    fontSize: 13,
    fontWeight: '400',
    color: 'rgba(0, 0, 0, 0.6)',
    lineHeight: 20,
  },
  floatingBubbleSeeAll: {
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginTop: 2,
  },
  floatingBubbleSeeAllText: {
    fontSize: 13,
    fontWeight: '500',
    color: '#7C4DFF',
  },
  chatBubble: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 12,
    paddingBottom: 14,
    gap: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.92)',
    borderRadius: 24,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: 'rgba(0, 0, 0, 0.06)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 16,
    elevation: 6,
  },
  chatInput: {
    flex: 1,
    height: 44,
    borderRadius: 22,
    paddingHorizontal: 18,
    paddingVertical: 10,
    fontSize: 15,
    color: '#1C1C1E',
    backgroundColor: '#F5F5F7',
    borderWidth: 1,
    borderColor: '#E5E5EA',
  },
  chatSendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#7C4DFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  navBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    zIndex: 10,
    flexDirection: 'row',
    backgroundColor: '#F5F5F7',
    paddingTop: 12,
    paddingBottom: 28,
    paddingHorizontal: 8,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E8E8EC',
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconWrap: {
    width: 52,
    height: 52,
    borderRadius: 26,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  iconWrapActive: {
    backgroundColor: 'rgba(124, 77, 255, 0.18)',
  },
  navLabel: {
    fontSize: 13,
    color: '#8E8E93',
    fontWeight: '500',
  },
  navLabelActive: {
    color: '#7C4DFF',
  },
});
