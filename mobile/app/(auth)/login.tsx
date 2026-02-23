import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  Alert,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '@/context/AuthContext';
import { Input, Button } from '@/components/ui';
import { colors, spacing, typography } from '@/theme';

export default function LoginScreen() {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Error', 'Ingresa tu usuario y contraseña');
      return;
    }
    setLoading(true);
    try {
      await login(username.trim(), password);
    } catch (err: any) {
      const msg = err.response?.data?.message || 'Usuario o contraseña incorrectos';
      Alert.alert('Error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.content}
      >
        <View style={styles.logoArea}>
          {/* TODO: reemplazar con logo real */}
          <View style={styles.logoPlaceholder}>
            <Text style={styles.logoText}>PROTEG</Text>
          </View>
          <Text style={styles.subtitle}>Mutualidad Proteg-rt</Text>
        </View>

        <View style={styles.form}>
          <Input
            label="Usuario"
            placeholder="tu.usuario"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="next"
          />

          <Input
            label="Contraseña"
            placeholder="••••••••"
            value={password}
            onChangeText={setPassword}
            secureTextEntry={!showPassword}
            returnKeyType="done"
            onSubmitEditing={handleLogin}
            rightIcon={
              <Pressable onPress={() => setShowPassword(!showPassword)}>
                <Text style={styles.eyeIcon}>{showPassword ? '🙈' : '👁️'}</Text>
              </Pressable>
            }
          />

          <Button
            title="INICIAR SESIÓN"
            onPress={handleLogin}
            loading={loading}
            size="lg"
            style={{ marginTop: spacing.md }}
          />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: spacing['3xl'],
  },
  logoArea: {
    alignItems: 'center',
    marginBottom: spacing['4xl'],
  },
  logoPlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 24,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  logoText: {
    color: colors.white,
    fontSize: 22,
    fontWeight: '800',
    letterSpacing: 2,
  },
  subtitle: {
    ...typography.body,
    color: colors.gray500,
  },
  form: {},
  eyeIcon: {
    fontSize: 20,
  },
});
