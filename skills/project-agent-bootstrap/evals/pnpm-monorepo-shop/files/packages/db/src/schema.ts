import { pgTable, serial, text, integer } from 'drizzle-orm/pg-core';

export const products = pgTable('products', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  priceCents: integer('price_cents').notNull(),
});
