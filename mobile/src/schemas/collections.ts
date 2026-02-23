import { z } from 'zod';

export const loginSchema = z.object({
  username: z.string().min(1, 'Ingresa tu usuario'),
  password: z.string().min(1, 'Ingresa tu contraseña'),
});
export type LoginForm = z.infer<typeof loginSchema>;

export const cobroSchema = z.object({
  amount: z
    .string()
    .min(1, 'Ingresa el monto cobrado')
    .refine((v) => !isNaN(parseFloat(v)) && parseFloat(v) > 0, 'El monto debe ser mayor a 0'),
  method: z.enum(['efectivo', 'deposito', 'transferencia'], {
    required_error: 'Selecciona un método de pago',
  }),
  receipt_number: z.string().min(1, 'Ingresa el número de recibo'),
});
export type CobroForm = z.infer<typeof cobroSchema>;

export const abonoSchema = z.object({
  amount: z
    .string()
    .min(1, 'Ingresa el monto del abono')
    .refine((v) => !isNaN(parseFloat(v)) && parseFloat(v) > 0, 'El monto debe ser mayor a 0'),
  method: z.enum(['efectivo', 'deposito', 'transferencia'], {
    required_error: 'Selecciona un método de pago',
  }),
  receipt_number: z.string().min(1, 'Ingresa el número de recibo'),
});
export type AbonoForm = z.infer<typeof abonoSchema>;

export const avisoSchema = z.object({
  reason: z.enum(['no_estaba', 'sin_efectivo', 'pagara_despues', 'otro'], {
    required_error: 'Selecciona qué ocurrió',
  }),
  reason_detail: z.string().optional(),
});
export type AvisoForm = z.infer<typeof avisoSchema>;

export const confirmCashSchema = z.object({
  received_amount: z
    .string()
    .min(1, 'Ingresa el monto recibido')
    .refine((v) => !isNaN(parseFloat(v)) && parseFloat(v) >= 0, 'Monto inválido'),
});
export type ConfirmCashForm = z.infer<typeof confirmCashSchema>;

export const rejectSchema = z.object({
  rejection_reason: z.string().min(1, 'Indica el motivo del rechazo'),
});
export type RejectForm = z.infer<typeof rejectSchema>;
