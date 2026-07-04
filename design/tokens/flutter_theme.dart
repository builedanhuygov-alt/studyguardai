// StudyGuard AI — Flutter Material 3 theme (generated from tokens.json).
import 'package:flutter/material.dart';

class SGColors {
  static const brand = Color(0xFF4F46E5);
  static const brandLight = Color(0xFF6366F1);
  static const coach = Color(0xFF7C3AED);
  static const growth = Color(0xFF10B981);
  static const streak = Color(0xFFF59E0B);
  static const success = Color(0xFF16A34A);
  static const warning = Color(0xFFD97706);
  static const danger = Color(0xFFDC2626);
  static const darkBg = Color(0xFF0B0E14);
  static const darkSurface = Color(0xFF141922);
  static const lightBg = Color(0xFFF7F8FA);
  static const lightSurface = Color(0xFFFFFFFF);
}

class SGRadius {
  static const sm = 10.0, md = 14.0, lg = 20.0, xl = 28.0, pill = 999.0;
}

class SGSpace {
  static const s1 = 4.0, s2 = 8.0, s3 = 12.0, s4 = 16.0, s6 = 24.0, s8 = 32.0;
}

ThemeData sgTheme(Brightness brightness) {
  final isDark = brightness == Brightness.dark;
  final scheme = ColorScheme.fromSeed(
    seedColor: SGColors.brand,
    brightness: brightness,
    secondary: SGColors.coach,
    tertiary: SGColors.growth,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: isDark ? SGColors.darkBg : SGColors.lightBg,
    fontFamily: 'Inter',
    cardTheme: CardTheme(
      elevation: 0,
      color: isDark ? SGColors.darkSurface : SGColors.lightSurface,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(SGRadius.md)),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(SGRadius.sm)),
        padding: const EdgeInsets.symmetric(horizontal: SGSpace.s6, vertical: SGSpace.s3),
      ),
    ),
    textTheme: const TextTheme(
      displaySmall: TextStyle(fontFamily: 'Newsreader', fontWeight: FontWeight.w600),
      titleLarge: TextStyle(fontWeight: FontWeight.w600),
    ),
  );
}
