import { TextStyle } from 'react-native';
import { colors } from './colors';

export const typography = {
  h1: { fontSize: 26, fontWeight: '700', color: colors.textDark, lineHeight: 34 } as TextStyle,
  h2: { fontSize: 22, fontWeight: '700', color: colors.textDark, lineHeight: 28 } as TextStyle,
  h3: { fontSize: 18, fontWeight: '700', color: colors.textDark, lineHeight: 24 } as TextStyle,
  body: { fontSize: 16, fontWeight: '400', color: colors.textDark, lineHeight: 22 } as TextStyle,
  bodyBold: { fontSize: 16, fontWeight: '700', color: colors.textDark, lineHeight: 22 } as TextStyle,
  caption: { fontSize: 13, fontWeight: '400', color: colors.textMedium, lineHeight: 18 } as TextStyle,
  captionBold: { fontSize: 13, fontWeight: '700', color: colors.textMedium, lineHeight: 18 } as TextStyle,
  small: { fontSize: 12, fontWeight: '400', color: colors.textMedium, lineHeight: 16 } as TextStyle,
  label: { fontSize: 11, fontWeight: '700', color: colors.white, letterSpacing: 0.5 } as TextStyle,
  money: { fontSize: 42, fontWeight: '800', color: colors.white, lineHeight: 50 } as TextStyle,
  moneyDark: { fontSize: 36, fontWeight: '800', color: colors.textDark } as TextStyle,
  sectionTitle: { fontSize: 18, fontWeight: '700', color: colors.textDark } as TextStyle,
};
