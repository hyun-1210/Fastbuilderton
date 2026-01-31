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
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { MaterialCommunityIcons } from '@expo/vector-icons';

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

const NAV_ITEMS = [
  { key: 'home', label: '홈', icon: 'home-circle-outline', iconFilled: 'home-circle' },
  { key: 'relations', label: '관계', icon: 'heart-circle-outline', iconFilled: 'heart-circle' },
  { key: 'profile', label: '프로필', icon: 'account-circle-outline', iconFilled: 'account-circle' },
];

function InsightStrip({ onViewAll }) {
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
    }, 4200);
    return () => clearInterval(interval);
  }, [fadeAnim]);

  return (
    <View style={styles.insightStrip}>
      <Animated.Text
        style={[styles.insightText, { opacity: fadeAnim }]}
        numberOfLines={1}
        ellipsizeMode="tail"
      >
        {INSIGHTS_DATA[index]}
      </Animated.Text>
      <TouchableOpacity
        style={styles.insightArrow}
        onPress={onViewAll}
        activeOpacity={0.7}
        hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}
      >
        <MaterialCommunityIcons
          name="chevron-right"
          size={24}
          color="#7C4DFF"
        />
      </TouchableOpacity>
    </View>
  );
}

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
    <View style={styles.floatingBubble}>
      <TouchableOpacity
        style={styles.floatingBubbleExpand}
        onPress={() => setExpanded(!expanded)}
        activeOpacity={0.7}
      >
        <MaterialCommunityIcons
          name={expanded ? 'chevron-down' : 'chevron-up'}
          size={20}
          color="#8E8E93"
        />
      </TouchableOpacity>
      <View style={styles.floatingBubbleNotifs}>
        {displayNotifications.map((item, index) => (
          <TouchableOpacity
            key={item.id}
            style={[
              styles.floatingBubbleNotifRow,
              index === displayNotifications.length - 1 && styles.floatingBubbleNotifRowLast,
            ]}
            onPress={() => onOpenNotification(item)}
            activeOpacity={0.6}
          >
            <MaterialCommunityIcons
              name={item.icon}
              size={18}
              color="#8E8E93"
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
            <MaterialCommunityIcons name="chevron-right" size={18} color="#7C4DFF" />
          </TouchableOpacity>
        )}
      </View>
      <View style={styles.floatingBubbleChat}>
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

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      // TODO: send message
      setChatMessage('');
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.mainContent}>
        <View style={styles.headerRow}>
          <Text style={styles.logo}>ANBU</Text>
        </View>
        {activeTab === 'home' ? (
          <ScrollView
            style={styles.homeScroll}
            contentContainerStyle={styles.homeScrollContent}
            showsVerticalScrollIndicator={false}
          >
            <InsightStrip onViewAll={() => setShowAllInsights(true)} />
          </ScrollView>
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
  mainContent: {
    flex: 1,
    marginHorizontal: 14,
    marginTop: 14,
    marginBottom: 10,
    borderRadius: 28,
    backgroundColor: 'rgba(255, 255, 255, 0.88)',
    overflow: 'hidden',
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 24,
    elevation: 6,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 52,
    paddingBottom: 14,
  },
  logo: {
    fontSize: 22,
    fontWeight: '700',
    color: '#7C4DFF',
    letterSpacing: 0.5,
  },
  insightStrip: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'stretch',
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 10,
    paddingVertical: 10,
    paddingLeft: 20,
    paddingRight: 10,
    backgroundColor: 'rgba(124, 77, 255, 0.12)',
    borderRadius: 24,
    borderWidth: 1,
    borderColor: 'rgba(124, 77, 255, 0.2)',
    shadowColor: '#7C4DFF',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.14,
    shadowRadius: 18,
    elevation: 4,
  },
  insightText: {
    flex: 1,
    fontSize: 15,
    fontWeight: '600',
    color: '#6B4EBB',
    lineHeight: 22,
    paddingRight: 8,
  },
  insightArrow: {
    padding: 6,
    marginLeft: 4,
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
    paddingBottom: 320,
    paddingHorizontal: 0,
  },
  tabPlaceholder: {
    flex: 1,
  },
  floatingBubbleWrap: {
    position: 'absolute',
    left: 20,
    right: 20,
    bottom: 124,
  },
  floatingBubble: {
    backgroundColor: 'rgba(255, 255, 255, 0.88)',
    borderRadius: 24,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: 'rgba(0, 0, 0, 0.06)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06,
    shadowRadius: 16,
    elevation: 6,
    overflow: 'hidden',
  },
  floatingBubbleExpand: {
    alignItems: 'center',
    paddingVertical: 6,
    paddingTop: 8,
  },
  floatingBubbleNotifs: {
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: 'rgba(0, 0, 0, 0.06)',
  },
  floatingBubbleNotifRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderBottomWidth: 0,
    backgroundColor: 'transparent',
  },
  floatingBubbleNotifRowLast: {
    borderBottomWidth: 0,
  },
  floatingBubbleNotifIcon: {
    marginRight: 10,
    opacity: 0.8,
  },
  floatingBubbleNotifText: {
    flex: 1,
    fontSize: 14,
    fontWeight: '400',
    color: '#3C3C43',
    lineHeight: 20,
    opacity: 0.95,
  },
  floatingBubbleSeeAll: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: 'rgba(0, 0, 0, 0.06)',
  },
  floatingBubbleSeeAllText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#7C4DFF',
  },
  floatingBubbleChat: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 14,
    paddingVertical: 12,
    paddingBottom: 14,
    gap: 10,
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
