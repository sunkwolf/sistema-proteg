import dayjs from 'dayjs';
import 'dayjs/locale/es';

dayjs.locale('es');

/** Formatea monto: "$1,200.00" */
export function formatMoney(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return `$${num.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/** Formatea fecha: "20/Feb" */
export function formatDateShort(date: string): string {
  return dayjs(date).format('DD/MMM').replace('.', '');
}

/** Formatea fecha completa: "Viernes 20 Feb" */
export function formatDateFull(date: string): string {
  return dayjs(date).format('dddd DD MMM').replace('.', '');
}

/** Formatea hora: "10:15 AM" */
export function formatTime(date: string): string {
  return dayjs(date).format('h:mm A');
}

/** Días de atraso (positivo = atrasado, negativo = por vencer) */
export function daysOverdue(dueDate: string): number {
  return dayjs().startOf('day').diff(dayjs(dueDate).startOf('day'), 'day');
}
