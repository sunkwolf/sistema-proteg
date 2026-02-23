import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'expo-router';
import { useAuthStore } from '@/store/auth';
import * as authApi from '@/api/auth';
import { loginSchema, LoginForm } from '@/schemas/collections';
import { Input, Button } from '@/components/ui';
import { Image } from 'react-native';
import { colors, spacing } from '@/theme';

export default function LoginScreen() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [loading, setLoading] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);

  const { control, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  });

  const navigateByRole = (role: string) => {
    if (role === 'gerente_cobranza' || role === 'auxiliar_cobranza') {
      router.replace('/(gerente)');
    } else {
      router.replace('/(cobrador)');
    }
  };

  const mockLogin = async (role: 'cobrador' | 'gerente_cobranza') => {
    const mockUsers = {
      cobrador: { id: 1, name: 'Edgar Martinez', username: 'edgar.m', role: 'cobrador' as const, zone: 'Zona Norte', avatar_url: null },
      gerente_cobranza: { id: 2, name: 'Gabriela Lopez', username: 'gaby.l', role: 'gerente_cobranza' as const, zone: null, avatar_url: null },
    };
    await setAuth(mockUsers[role], 'mock-token-123', 'mock-refresh-456');
    navigateByRole(role);
  };

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    try {
      const result = await authApi.login(data.username, data.password);
      await setAuth(result.user, result.token, result.refresh_token);
      navigateByRole(result.user.role);
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Usuario o contraseña incorrectos';
      Alert.alert('Error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={['#4A3AFF', '#6C5CE7', '#8B5CF6']}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={styles.gradient}
    >
      <SafeAreaView style={styles.safe}>
        <KeyboardAvoidingView
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.content}
        >
          {/* Logo */}
          <View style={styles.logoArea}>
            <Image
              source={require('../../../assets/logo-protegrt.png')}
              style={styles.logoImage}
              resizeMode="contain"
            />
            <Text style={styles.logoTitle}>Proteg-rt</Text>
            <Text style={styles.logoSubtitle}>Mutualidad de Seguros</Text>
          </View>

          {/* Form Card */}
          <View style={styles.formCard}>
            <Text style={styles.formTitle}>Iniciar Sesión</Text>
            <Text style={styles.formSubtitle}>Ingresa tus credenciales para continuar</Text>

            <Controller
              control={control}
              name="username"
              render={({ field: { onChange, value } }) => (
                <Input
                  label="USUARIO"
                  placeholder="tu.usuario"
                  value={value}
                  onChangeText={onChange}
                  autoCapitalize="none"
                  autoCorrect={false}
                  returnKeyType="next"
                  error={errors.username?.message}
                />
              )}
            />

            <Controller
              control={control}
              name="password"
              render={({ field: { onChange, value } }) => (
                <Input
                  label="CONTRASEÑA"
                  placeholder="••••••••"
                  value={value}
                  onChangeText={onChange}
                  secureTextEntry={!showPassword}
                  returnKeyType="done"
                  error={errors.password?.message}
                  rightIcon={
                    <Pressable onPress={() => setShowPassword(!showPassword)}>
                      <Text style={{ fontSize: 18 }}>{showPassword ? '🙈' : '👁️'}</Text>
                    </Pressable>
                  }
                />
              )}
            />

            <Button
              title="INICIAR SESIÓN"
              onPress={handleSubmit(onSubmit)}
              loading={loading}
              size="lg"
              style={{ marginTop: spacing.sm }}
            />

            <Pressable style={styles.biometricBtn}>
              <Text style={styles.biometricText}>🔑 Usar biometría</Text>
            </Pressable>

            {/* Mock login buttons for development */}
            <View style={styles.mockDivider}>
              <View style={styles.mockLine} />
              <Text style={styles.mockDividerText}>DEMO</Text>
              <View style={styles.mockLine} />
            </View>
            <Pressable style={styles.mockBtn} onPress={() => mockLogin('cobrador')}>
              <Text style={styles.mockBtnText}>📋 Entrar como Cobrador</Text>
            </Pressable>
            <Pressable style={[styles.mockBtn, styles.mockBtnGerente]} onPress={() => mockLogin('gerente_cobranza')}>
              <Text style={styles.mockBtnText}>👔 Entrar como Gerente</Text>
            </Pressable>
          </View>

          <Text style={styles.version}>v0.1.0-dev</Text>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  gradient: { flex: 1 },
  safe: { flex: 1 },
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  logoArea: {
    alignItems: 'center',
    marginBottom: 32,
  },
  logoImage: {
    width: 100,
    height: 100,
    marginBottom: 16,
  },
  logoTitle: {
    fontSize: 32,
    fontWeight: '800',
    color: colors.white,
    letterSpacing: 1,
  },
  logoSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.7)',
    marginTop: 4,
  },
  formCard: {
    backgroundColor: colors.white,
    borderRadius: 24,
    paddingHorizontal: 24,
    paddingVertical: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 30,
    elevation: 10,
  },
  formTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.textDark,
    marginBottom: 4,
  },
  formSubtitle: {
    fontSize: 14,
    color: colors.textMedium,
    marginBottom: 24,
  },
  biometricBtn: {
    alignItems: 'center',
    marginTop: 20,
    padding: 12,
  },
  biometricText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.primary,
  },
  version: {
    textAlign: 'center',
    color: 'rgba(255,255,255,0.4)',
    fontSize: 12,
    marginTop: 24,
  },
  mockDivider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 12,
  },
  mockLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#E0E0EA',
  },
  mockDividerText: {
    marginHorizontal: 12,
    fontSize: 11,
    fontWeight: '700',
    color: '#B0B0C0',
    letterSpacing: 1,
  },
  mockBtn: {
    backgroundColor: '#F0EEFF',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#D8D4FF',
  },
  mockBtnGerente: {
    backgroundColor: '#FFF0E6',
    borderColor: '#FFD4B0',
  },
  mockBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
  },
});
