// Standard API Response envelope
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

// User & Auth types
export type UserRole = 'USER' | 'ADMIN';

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone_number: string;
  role: UserRole;
  is_active: boolean;
  avatar_url?: string | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Category
export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string | null;
}

// Listing Types
export type TransactionType = 'SALE' | 'RENT';
export type ListingStatus = 'DRAFT' | 'PENDING_APPROVAL' | 'APPROVED' | 'REJECTED' | 'EXPIRED' | 'HIDDEN';

export interface ListingImage {
  id?: number;
  image_url: string;
  public_id: string;
  is_thumbnail?: boolean;
  display_order?: number;
}

export interface ListingCard {
  id: number;
  title: string;
  price: number;
  price_unit: string;
  area: number;
  bedrooms?: number | null;
  bathrooms?: number | null;
  address_text: string;
  province: string;
  district: string;
  transaction_type: TransactionType;
  category_id: number;
  category_name: string;
  thumbnail_url?: string | null;
  status: ListingStatus;
  view_count: number;
  published_at?: string | null;
  created_at: string;
}

export interface ListingDetail {
  id: number;
  user_id: number;
  title: string;
  description: string;
  category_id: number;
  category_name: string;
  transaction_type: TransactionType;
  price: number;
  price_unit: string;
  area: number;
  bedrooms?: number | null;
  bathrooms?: number | null;
  direction?: string | null;
  legal_status?: string | null;
  address_text: string;
  province: string;
  district: string;
  ward?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  status: ListingStatus;
  rejection_reason?: string | null;
  view_count: number;
  published_at?: string | null;
  expired_at?: string | null;
  created_at: string;
  updated_at: string;
  images: ListingImage[];
  features: string[];
  owner_id: number;
  owner_name: string;
  owner_phone: string;
  owner_avatar?: string | null;
  is_favorite: boolean;
}

export interface ListingCreatePayload {
  title: string;
  description: string;
  category_id: number;
  transaction_type: TransactionType;
  price: number;
  price_unit: string;
  area: number;
  bedrooms?: number | null;
  bathrooms?: number | null;
  direction?: string | null;
  legal_status?: string | null;
  address_text: string;
  province: string;
  district: string;
  ward?: string | null;
  features?: string[];
  images: ListingImage[];
  is_draft: boolean;
}

export interface ListingSearchParams {
  keyword?: string;
  category_id?: number;
  transaction_type?: TransactionType;
  min_price?: number;
  max_price?: number;
  min_area?: number;
  max_area?: number;
  province?: string;
  district?: string;
  bedrooms?: number;
  sort_by?: 'newest' | 'price_asc' | 'price_desc' | 'area_asc' | 'area_desc';
  page?: number;
  size?: number;
}

// Interaction Types
export interface InquiryCreatePayload {
  listing_id: number;
  sender_name: string;
  sender_phone: string;
  sender_email?: string;
  message: string;
}

export interface Inquiry {
  id: number;
  listing_id: number;
  listing_title: string;
  seeker_id?: number | null;
  sender_name: string;
  sender_phone: string;
  sender_email?: string | null;
  message: string;
  status: 'PENDING' | 'CONTACTED' | 'CLOSED';
  created_at: string;
}

// Health status for connection check
export interface DatabaseHealth {
  status: 'connected' | 'disconnected';
  dialect: string;
  latency_ms: number;
  error: string | null;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  app_name: string;
  environment: string;
  version: string;
  database: DatabaseHealth;
  timestamp: string;
}

export interface ScoreBreakdown {
  price_score: number;
  location_score: number;
  category_score: number;
  area_score: number;
  bedroom_score: number;
  feature_score: number;
  total_score: number;
  match_percentage: number;
}

export interface RecommendedListingItem extends ListingCard {
  match_score: number;
  match_percentage: number;
  score_breakdown: ScoreBreakdown;
  match_reasons: string[];
}

