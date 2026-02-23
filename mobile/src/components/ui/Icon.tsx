import React from 'react';
import { MaterialCommunityIcons, Ionicons, Feather, MaterialIcons } from '@expo/vector-icons';

// Centralized icon mapping — one place to change all icons
const ICON_MAP = {
  // Navigation & Actions
  back: { lib: 'Ionicons', name: 'chevron-back', size: 24 },
  menu: { lib: 'Feather', name: 'menu', size: 22 },
  bell: { lib: 'Ionicons', name: 'notifications', size: 24 },
  bellBadge: { lib: 'Ionicons', name: 'notifications', size: 24 },
  settings: { lib: 'Ionicons', name: 'settings-outline', size: 22 },
  more: { lib: 'Feather', name: 'more-vertical', size: 20 },
  search: { lib: 'Feather', name: 'search', size: 20 },
  chevronRight: { lib: 'Feather', name: 'chevron-right', size: 20 },
  close: { lib: 'Feather', name: 'x', size: 22 },

  // Tabs
  home: { lib: 'Ionicons', name: 'home', size: 24 },
  homeOutline: { lib: 'Ionicons', name: 'home-outline', size: 24 },
  folios: { lib: 'Ionicons', name: 'document-text', size: 24 },
  foliosOutline: { lib: 'Ionicons', name: 'document-text-outline', size: 24 },
  route: { lib: 'MaterialCommunityIcons', name: 'map-marker-path', size: 24 },
  routeOutline: { lib: 'MaterialCommunityIcons', name: 'map-marker-path', size: 24 },
  proposals: { lib: 'Ionicons', name: 'clipboard', size: 24 },
  proposalsOutline: { lib: 'Ionicons', name: 'clipboard-outline', size: 24 },
  cash: { lib: 'MaterialCommunityIcons', name: 'cash-multiple', size: 24 },

  // Stats & Dashboard
  collections: { lib: 'Ionicons', name: 'receipt', size: 20 },
  money: { lib: 'MaterialCommunityIcons', name: 'cash', size: 20 },
  pending: { lib: 'MaterialCommunityIcons', name: 'clock-outline', size: 20 },
  commission: { lib: 'MaterialCommunityIcons', name: 'percent', size: 20 },
  approved: { lib: 'Ionicons', name: 'checkmark-circle', size: 20 },
  rejected: { lib: 'Ionicons', name: 'close-circle', size: 20 },
  corrected: { lib: 'MaterialCommunityIcons', name: 'wrench', size: 20 },

  // Forms & Actions
  phone: { lib: 'Feather', name: 'phone', size: 18 },
  navigate: { lib: 'MaterialCommunityIcons', name: 'navigation-variant', size: 18 },
  camera: { lib: 'Feather', name: 'camera', size: 22 },
  scan: { lib: 'MaterialCommunityIcons', name: 'qrcode-scan', size: 20 },
  print: { lib: 'Feather', name: 'printer', size: 18 },
  send: { lib: 'Feather', name: 'send', size: 18 },
  check: { lib: 'Feather', name: 'check', size: 18 },
  checkCircle: { lib: 'Ionicons', name: 'checkmark-circle', size: 24 },
  warning: { lib: 'Ionicons', name: 'warning', size: 18 },
  alert: { lib: 'Ionicons', name: 'alert-circle', size: 18 },
  info: { lib: 'Ionicons', name: 'information-circle', size: 18 },
  edit: { lib: 'Feather', name: 'edit-2', size: 18 },
  location: { lib: 'Ionicons', name: 'location', size: 18 },
  time: { lib: 'Ionicons', name: 'time', size: 16 },
  calendar: { lib: 'Ionicons', name: 'calendar', size: 16 },
  person: { lib: 'Ionicons', name: 'person', size: 18 },

  // Payment methods
  cashMethod: { lib: 'MaterialCommunityIcons', name: 'cash', size: 24 },
  deposit: { lib: 'MaterialCommunityIcons', name: 'bank', size: 24 },
  transfer: { lib: 'MaterialCommunityIcons', name: 'cellphone', size: 24 },

  // Vehicles & Policy
  car: { lib: 'Ionicons', name: 'car', size: 18 },
  shield: { lib: 'Ionicons', name: 'shield-checkmark', size: 18 },

  // Route
  mapPin: { lib: 'Ionicons', name: 'location', size: 16 },
  play: { lib: 'Ionicons', name: 'play-circle', size: 24 },
  navigationArrow: { lib: 'MaterialCommunityIcons', name: 'navigation-variant', size: 18 },
} as const;

export type IconName = keyof typeof ICON_MAP;

interface IconProps {
  name: IconName;
  size?: number;
  color?: string;
}

const LIBS: Record<string, any> = {
  MaterialCommunityIcons,
  Ionicons,
  Feather,
  MaterialIcons,
};

export function Icon({ name, size, color = '#1A1A1A' }: IconProps) {
  const config = ICON_MAP[name];
  if (!config) return null;
  const Lib = LIBS[config.lib];
  return <Lib name={config.name} size={size || config.size} color={color} />;
}
